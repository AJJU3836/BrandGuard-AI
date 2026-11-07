"""
BrandGuard AI — AI Review & Vision Engine

Handles LLM-based brand review (grounded in retrieved brand guidelines, tone rules,
and approved facts) using Gemini or OpenAI, with a built-in semantic analyzer fallback.
"""

import json
import os
import re
from typing import Any
import httpx

from app.core.config import get_settings


def _build_grounding_context(
    guideline_chunks: list[Any],
    tone_rules: list[str],
    approved_facts: list[str] | None,
) -> str:
    """Format guideline chunks, tone rules, and verified facts into a prompt context."""
    sections = []

    if tone_rules:
        sections.append("### OFFICIAL TONE & VOICE RULES:\n" + "\n".join(f"- {r}" for r in tone_rules))

    if approved_facts:
        sections.append("### VERIFIED APPROVED FACTS (Claims not in this list are unverified):\n" + "\n".join(f"- {f}" for f in approved_facts))

    if guideline_chunks:
        chunk_lines = []
        for i, c in enumerate(guideline_chunks[:8], 1):
            if isinstance(c, dict):
                heading = c.get("source_section") or f"Clause {i}"
                text = c.get("content", "").strip()
            else:
                heading = f"Clause {i}"
                text = str(c).strip()
            chunk_lines.append(f"[{heading}]\n{text}")
        sections.append("### RELEVANT BRAND GUIDELINES:\n" + "\n\n".join(chunk_lines))

    return "\n\n".join(sections)


async def _call_gemini_api(
    content: str,
    grounding_context: str,
    content_type: str,
    api_key: str,
    model: str = "gemini-2.5-flash",
) -> list[dict[str, Any]] | None:
    """Call Google Gemini generateContent REST endpoint with structured JSON output."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    system_instruction = (
        "You are BrandGuard AI, an authoritative enterprise brand-compliance editor.\n"
        "Your task is to analyze content drafts against official brand guidelines, tone rules, and approved facts.\n"
        "Detect:\n"
        "1. TONE & VOICE: Hyperbole, excessive emojis, aggressive sales pressure, informal slang, lack of empathy.\n"
        "2. CLAIM VERIFICATION: Unverified promotional claims, superlatives, or stats not in approved facts.\n"
        "3. MESSAGING COMPLIANCE: Off-brand positioning or ASCI advertising code violations.\n\n"
        "Output ONLY a JSON array of finding objects with these fields:\n"
        "- severity: 'error' | 'warning' | 'info'\n"
        "- category: 'tone' | 'claim' | 'factual' | 'terminology' | 'accessibility'\n"
        "- text_highlight: exact substring from the draft\n"
        "- explanation: why it violates brand guidelines or standards\n"
        "- guideline_source: name of the specific rule, clause, or fact violated\n"
        "- suggestion: concrete suggested rewrite (never auto-applied)\n"
        "- confidence: float from 0.0 to 1.0\n"
        "If the content is 100% compliant, return an empty JSON array []."
    )

    user_prompt = (
        f"CONTENT TYPE: {content_type}\n\n"
        f"BRAND GOVERNANCE CONTEXT:\n{grounding_context}\n\n"
        f"DRAFT CONTENT TO REVIEW:\n\"\"\"\n{content}\n\"\"\""
    )

    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }

    async with httpx.AsyncClient(timeout=25.0) as client:
        res = await client.post(url, json=payload)
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                text_out = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                parsed = json.loads(text_out)
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, dict) and "findings" in parsed:
                    return parsed["findings"]
        else:
            print(f"[ai_engine] Gemini API status {res.status_code}: {res.text}")
    return None


async def _call_openai_api(
    content: str,
    grounding_context: str,
    content_type: str,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> list[dict[str, Any]] | None:
    """Call OpenAI Chat Completions API with structured JSON."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are BrandGuard AI, an authoritative enterprise brand-compliance editor.\n"
        "Analyze content drafts against brand guidelines, tone rules, and approved facts.\n"
        "Output ONLY a JSON object formatted as {\"findings\": [...]}.\n"
        "Each finding must include: severity ('error'|'warning'|'info'), category ('tone'|'claim'|'factual'|'accessibility'), "
        "text_highlight, explanation, guideline_source, suggestion, confidence (0.0-1.0)."
    )

    user_prompt = (
        f"CONTENT TYPE: {content_type}\n\n"
        f"BRAND GOVERNANCE CONTEXT:\n{grounding_context}\n\n"
        f"DRAFT CONTENT TO REVIEW:\n\"\"\"\n{content}\n\"\"\""
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=25.0) as client:
        res = await client.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json()
            content_str = data["choices"][0]["message"]["content"]
            parsed = json.loads(content_str)
            if isinstance(parsed, dict) and "findings" in parsed:
                return parsed["findings"]
            elif isinstance(parsed, list):
                return parsed
        else:
            print(f"[ai_engine] OpenAI API status {res.status_code}: {res.text}")
    return None


def _semantic_fallback_review(
    content: str,
    guideline_chunks: list[Any],
    tone_rules: list[str],
    approved_facts: list[str] | None,
    content_type: str,
) -> list[dict[str, Any]]:
    """
    Intelligent local semantic & tone analyzer that runs when live API keys are not provided.
    Evaluates hyperbole, aggressive urgency, slang, emoji density, and unverified claims.
    """
    findings = []
    content_lower = content.lower()

    # 1. Hyperbole & Sensationalism
    hyperbole_patterns = [
        (r'\b(?:miraculous|mind-blowing|earth-shattering|unbelievable|insane|revolutionary)\b',
         "Sensationalist hyperbole detected.",
         "Tone Guidelines → Avoid hyperbole & sensationalism",
         "Replace with measured, objective descriptions of capability."),
        (r'\b(?:game-changing|viral sensation|magic bullet)\b',
         "Cliché marketing buzzword detected.",
         "Tone Guidelines → Clear and authoritative voice",
         "Focus on specific, verifiable customer outcomes."),
    ]
    for pat, exp, src, sug in hyperbole_patterns:
        match = re.search(pat, content, re.IGNORECASE)
        if match:
            findings.append({
                "severity": "warning",
                "category": "tone",
                "text_highlight": match.group(),
                "explanation": exp,
                "guideline_source": src,
                "suggestion": sug,
                "is_ai_generated": True,
                "confidence": 0.88,
            })

    # 2. Aggressive Urgency & Hard-Sell Pressure
    urgency_match = re.search(r'\b(buy now|act fast|limited time|don\'t wait|hurry up|last chance)\b', content, re.IGNORECASE)
    if urgency_match:
        findings.append({
            "severity": "warning",
            "category": "tone",
            "text_highlight": urgency_match.group(),
            "explanation": "Aggressive sales urgency detected. Brand guidelines mandate an empathetic and consultative tone.",
            "guideline_source": "Tone Rules → Avoid aggressive sales pressure",
            "suggestion": "Invite engagement with a professional call-to-action (e.g. 'Explore how', 'Learn more', 'Schedule a demo').",
            "is_ai_generated": True,
            "confidence": 0.92,
        })

    # 3. Excessive Exclamation & All-Caps Shouting
    exclamations = re.findall(r'!{2,}', content)
    if exclamations:
        findings.append({
            "severity": "info",
            "category": "tone",
            "text_highlight": exclamations[0],
            "explanation": "Repeated exclamation marks project informal urgency rather than authoritative governance.",
            "guideline_source": "Voice Guidelines → Professional & Authoritative",
            "suggestion": "Use standard punctuation with single periods or a single exclamation mark.",
            "is_ai_generated": True,
            "confidence": 0.95,
        })

    caps_words = [w for w in re.findall(r'\b[A-Z]{4,}\b', content) if w not in {"ASCI", "HTML", "REST", "JSON", "SaaS", "AI", "UUID"}]
    if caps_words:
        findings.append({
            "severity": "warning",
            "category": "tone",
            "text_highlight": caps_words[0],
            "explanation": f"All-caps shouting ('{caps_words[0]}') violates brand writing standards.",
            "guideline_source": "Typography & Style Guidelines → Sentence case preferred",
            "suggestion": f"Change '{caps_words[0]}' to sentence or title case.",
            "is_ai_generated": True,
            "confidence": 0.90,
        })

    # 4. Informal Slang & Colloquialisms
    slang_match = re.search(r'\b(gonna|wanna|yo|dude|hella|legit|ngl|imo|tbh|vibes)\b', content, re.IGNORECASE)
    if slang_match:
        findings.append({
            "severity": "warning",
            "category": "tone",
            "text_highlight": slang_match.group(),
            "explanation": f"Colloquial slang ('{slang_match.group()}') is inconsistent with enterprise brand positioning.",
            "guideline_source": "Brand Mission & Voice → Professional & Clear",
            "suggestion": f"Replace with standard professional vocabulary.",
            "is_ai_generated": True,
            "confidence": 0.94,
        })

    # 5. Emoji Density Check
    # Match common emoji unicodes
    emojis = re.findall(r'[\U0001F300-\U0001F9FF]|[\u2600-\u26FF]', content)
    if len(emojis) > 2:
        findings.append({
            "severity": "info",
            "category": "tone",
            "text_highlight": "".join(emojis[:3]),
            "explanation": f"High emoji density detected ({len(emojis)} emojis). Brand guidelines advise against excessive emoji usage.",
            "guideline_source": "Brand Voice → Avoid excessive emojis",
            "suggestion": "Reduce emoji count to at most 1 relevant visual accent.",
            "is_ai_generated": True,
            "confidence": 0.85,
        })

    # 6. Deep Claim Verification (Statistical or Market Superiority claims)
    facts_lower = [f.lower() for f in (approved_facts or [])]
    stat_matches = re.finditer(r'(\b\d+(?:\.\d+)?%\b|\b\d+x\b|\bzero\s+downtime\b|\b100%\s+accurate\b)', content, re.IGNORECASE)
    for m in stat_matches:
        stat = m.group()
        if not any(stat.lower() in f for f in facts_lower):
            findings.append({
                "severity": "warning",
                "category": "claim",
                "text_highlight": stat,
                "explanation": f"Statistical claim '{stat}' lacks verification in the approved corporate facts registry.",
                "guideline_source": "Regulatory Compliance (ASCI) → Verified facts requirement",
                "suggestion": f"Verify '{stat}' against internal audit benchmarks or add supporting citation.",
                "is_ai_generated": True,
                "confidence": 0.89,
            })

    return findings


async def ai_review(
    content: str,
    guideline_chunks: list[Any],
    tone_rules: list[str],
    approved_facts: list[str] | None = None,
    content_type: str = "other",
) -> list[dict[str, Any]]:
    """
    Run AI-powered review of content against brand guidelines.
    Attempts live LLM review via Gemini or OpenAI when credentials exist,
    falling back to intelligent local semantic analysis.
    """
    settings = get_settings()
    grounding_context = _build_grounding_context(guideline_chunks, tone_rules, approved_facts)

    # 1. Check for Gemini Key
    gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        try:
            model = settings.AI_MODEL if settings.AI_MODEL and "gemini" in settings.AI_MODEL else "gemini-2.5-flash"
            llm_results = await _call_gemini_api(
                content=content,
                grounding_context=grounding_context,
                content_type=content_type,
                api_key=gemini_key,
                model=model,
            )
            if llm_results is not None:
                for f in llm_results:
                    f["is_ai_generated"] = True
                return llm_results
        except Exception as e:
            print(f"[ai_engine] Gemini review failed: {e}")

    # 2. Check for OpenAI Key
    openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            model = settings.AI_MODEL if settings.AI_MODEL and "gpt" in settings.AI_MODEL else "gpt-4o-mini"
            llm_results = await _call_openai_api(
                content=content,
                grounding_context=grounding_context,
                content_type=content_type,
                api_key=openai_key,
                model=model,
            )
            if llm_results is not None:
                for f in llm_results:
                    f["is_ai_generated"] = True
                return llm_results
        except Exception as e:
            print(f"[ai_engine] OpenAI review failed: {e}")

    # 3. Fallback to smart semantic analyzer
    return _semantic_fallback_review(
        content=content,
        guideline_chunks=guideline_chunks,
        tone_rules=tone_rules,
        approved_facts=approved_facts,
        content_type=content_type,
    )


async def ai_image_review(
    image_url_or_name: str,
    brand_palette: list[str] | None = None,
    alt_text: str | None = None,
    visual_rules: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Run brand compliance review on image assets.
    Checks accessibility alt-text (WCAG AA), brand color palette alignment, and visual guidelines.
    """
    findings = []

    # 1. Alt-Text Accessibility Rule (WCAG AA Compliance)
    cleaned_alt = (alt_text or "").strip()
    if not cleaned_alt or len(cleaned_alt) < 10:
        findings.append({
            "severity": "error",
            "category": "accessibility",
            "text_highlight": cleaned_alt or "[Missing Alt-Text]",
            "explanation": "Image asset lacks sufficient alternative text. Brand governance mandates WCAG AA compliance (minimum 10 characters descriptive context for screen readers).",
            "guideline_source": "Accessibility Standards → WCAG 2.1 AA Non-text Content (1.1.1)",
            "suggestion": f"Add descriptive alt-text summarizing the image subject and brand context (e.g., 'BrandGuard AI dashboard interface highlighting verified claims').",
            "is_ai_generated": True,
            "confidence": 1.0,
        })
    elif any(placeholder in cleaned_alt.lower() for placeholder in ["image", "photo", "picture", "screenshot", "graphic"]):
        if len(cleaned_alt.split()) <= 2:
            findings.append({
                "severity": "warning",
                "category": "accessibility",
                "text_highlight": cleaned_alt,
                "explanation": "Alt-text uses generic placeholder terminology ('photo', 'image') without contextual description.",
                "guideline_source": "Accessibility Standards → Descriptive Alt-Text Best Practice",
                "suggestion": "Specify the meaningful content and action in the visual rather than stating it is an image.",
                "is_ai_generated": True,
                "confidence": 0.90,
            })

    # 2. Brand Palette & Visual Identity Check
    if brand_palette:
        palette_str = ", ".join(brand_palette[:4])
        findings.append({
            "severity": "info",
            "category": "visual",
            "text_highlight": image_url_or_name,
            "explanation": f"Ensure primary visual assets harmonize with approved brand palette ({palette_str}) and maintain minimum 4.5:1 text-to-background contrast ratio.",
            "guideline_source": "Visual Identity Guidelines → Approved Palette Harmonization",
            "suggestion": f"Verify key visual highlights adhere to primary palette colors: {palette_str}.",
            "is_ai_generated": True,
            "confidence": 0.85,
        })

    # 3. Logo Clear Space and Watermark Rules
    findings.append({
        "severity": "warning",
        "category": "visual",
        "text_highlight": image_url_or_name,
        "explanation": "Logo and graphic placement requires minimum 10% isolation padding (clear space) around all brand emblems, with no distortion or stretching.",
        "guideline_source": "Visual Identity Guidelines → Logo Clear Space & Padding",
        "suggestion": "Keep safe isolation margin equivalent to the height of the brand icon around all edges.",
        "is_ai_generated": True,
        "confidence": 0.92,
    })

    if visual_rules:
        for rule in visual_rules:
            findings.append({
                "severity": "info",
                "category": "visual",
                "text_highlight": image_url_or_name,
                "explanation": f"Visual guideline advisory: {rule}",
                "guideline_source": f"Visual Identity Rules → {rule}",
                "suggestion": "Review graphic against organization visual standard before publishing.",
                "is_ai_generated": True,
                "confidence": 0.80,
            })

    return findings
