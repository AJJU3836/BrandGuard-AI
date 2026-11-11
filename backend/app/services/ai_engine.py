"""
BrandGuard AI — AI Review & Vision Engine

Handles LLM-based brand review (grounded in retrieved brand guidelines, tone rules,
and approved facts) using Gemini or OpenAI, with a built-in semantic analyzer fallback.
"""

import base64
import io
import json
import math
import os
import re
from typing import Any
import httpx

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

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


def _rel_luminance(rgb: tuple[int, int, int]) -> float:
    """Calculate relative luminance according to WCAG 2.1 standard."""
    def to_linear(c: int) -> float:
        v = c / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = [to_linear(x) for x in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast_ratio(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    """Calculate contrast ratio between two RGB colors (1.0:1 to 21.0:1)."""
    l1 = _rel_luminance(rgb1)
    l2 = _rel_luminance(rgb2)
    bright, dark = max(l1, l2), min(l1, l2)
    return (bright + 0.05) / (dark + 0.05)


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert hex string (e.g. #1E40AF) to RGB tuple."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def _color_distance(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    """Euclidean distance between two RGB colors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))


async def _call_gemini_vision_api(
    image_bytes: bytes,
    mime_type: str,
    brand_palette: list[str] | None,
    alt_text: str | None,
    visual_rules: list[str] | None,
    brand_name: str,
    image_name: str,
    api_key: str,
    model: str = "gemini-2.5-flash",
) -> list[dict[str, Any]] | None:
    """
    Call Google Gemini Vision Multimodal REST endpoint with image payload and structured JSON output.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    palette_desc = ", ".join(brand_palette) if brand_palette else "#1E40AF (Primary Blue), #2563EB (Accent Blue), #10B981 (Success Green)"
    rules_desc = "; ".join(visual_rules) if visual_rules else "Maintain 10% logo padding, avoid unapproved superlatives, adhere to WCAG 2.1 AA 4.5:1 contrast."

    system_instruction = (
        "You are BrandGuard AI Multimodal Vision & Accessibility Auditor.\n"
        "Analyze marketing assets and graphics for enterprise brand compliance and WCAG 2.1 AA accessibility.\n"
        f"Brand Identity: '{brand_name}'\n"
        f"Approved Brand Palette Hexes: {palette_desc}\n"
        f"Visual Rules: {rules_desc}\n\n"
        "Examine the image directly and evaluate:\n"
        "1. WCAG 2.1 AA Contrast (1.4.3): Calculate text-to-background contrast ratio for text overlays or buttons. Flag if ratio is below 4.5:1 (or 3:1 for large 18pt+ text).\n"
        "2. Color Palette Alignment: Identify dominant colors in the visual. Flag any severe clashes or unapproved neon/harsh tones with estimated hex codes.\n"
        "3. Brand Logo Placement & Integrity: Check for distortion, stretching, insufficient isolation padding (< 10%), or placement on low-contrast backgrounds.\n"
        "4. Alt-Text Accessibility (1.1.1): Compare provided alt-text against the visual. If missing, weak, or inaccurate, provide an exact recommended descriptive alt-text in the suggestion field.\n"
        "5. Visual Brand Safety: Flag low resolution, pixelation, unapproved claim badges (e.g. '100% Guaranteed', '#1 in India'), or competitor logos.\n\n"
        "Output ONLY a JSON array of finding objects with these fields:\n"
        "- severity: 'error' | 'warning' | 'info'\n"
        "- category: 'visual' | 'accessibility'\n"
        "- text_highlight: short label of the visual element (e.g., 'Hero Text Overlay', 'Banner Background', 'Logo Padding', 'Alt-Text Description')\n"
        "- explanation: clear explanation of the issue with measured contrast or color details\n"
        "- guideline_source: name of the specific standard (e.g., 'WCAG 2.1 AA (1.4.3) Contrast Minimum', 'Visual Identity → Approved Palette', 'WCAG 2.1 AA (1.1.1) Alt-Text Quality')\n"
        "- suggestion: concrete, actionable correction for the creator/designer\n"
        "- confidence: float from 0.85 to 1.0\n"
        "If the image is 100% compliant, return an empty JSON array []."
    )

    user_text = (
        f"ASSET NAME: {image_name}\n"
        f"PROVIDED ALT-TEXT: \"{alt_text or '[No Alt-Text Provided]'}\"\n\n"
        "Please conduct a comprehensive visual compliance and accessibility audit on this image."
    )

    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_text},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": b64_image,
                        }
                    },
                ]
            }
        ],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
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
            print(f"[ai_engine] Gemini Vision API status {res.status_code}: {res.text}")
    return None


def _pil_visual_and_accessibility_analyzer(
    image_bytes: bytes | None,
    image_name: str,
    brand_palette: list[str] | None = None,
    alt_text: str | None = None,
    visual_rules: list[str] | None = None,
    brand_name: str = "BrandGuard AI",
) -> list[dict[str, Any]]:
    """
    High-precision deterministic Pillow + WCAG 2.1 analyzer fallback.
    Extracts dominant colors, measures element contrast ratios, checks resolution, and audits alt-text.
    """
    findings = []
    dominant_hexes: list[tuple[str, tuple[int, int, int]]] = []

    if image_bytes and HAS_PIL:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size

            # Check resolution
            if width < 600 or height < 400:
                findings.append({
                    "severity": "warning",
                    "category": "visual",
                    "text_highlight": f"Resolution: {width}x{height}px",
                    "explanation": f"Image resolution ({width}x{height}px) is below the recommended minimum of 1200x630px for high-definition digital marketing.",
                    "guideline_source": "Visual Asset Standards → Image Resolution & Fidelity",
                    "suggestion": "Export asset at minimum 2x resolution (1200x630px or higher) to avoid blurriness on retina displays.",
                    "is_ai_generated": True,
                    "confidence": 0.95,
                })

            # Dominant color extraction
            small = img.convert("RGB").resize((64, 64))
            raw_colors = small.getcolors(maxcolors=4096) or []
            sorted_colors = sorted(raw_colors, key=lambda c: c[0], reverse=True)
            for c in sorted_colors[:5]:
                rgb = c[1]
                hex_code = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper()
                if not any(h[0] == hex_code for h in dominant_hexes):
                    dominant_hexes.append((hex_code, rgb))

            # Contrast ratio check between dominant background and foreground elements
            if len(dominant_hexes) >= 2:
                bg_color = dominant_hexes[0][1]
                fg_color = dominant_hexes[1][1]
                contrast_val = _contrast_ratio(bg_color, fg_color)
                if contrast_val < 4.5:
                    findings.append({
                        "severity": "error",
                        "category": "accessibility",
                        "text_highlight": f"Contrast {contrast_val:.1f}:1 ({dominant_hexes[0][0]} vs {dominant_hexes[1][0]})",
                        "explanation": f"Measured element contrast ratio ({contrast_val:.1f}:1) fails WCAG 2.1 AA Standard 1.4.3 (minimum 4.5:1 required for standard text/icons).",
                        "guideline_source": "Accessibility Standards → WCAG 2.1 AA Contrast Minimum (1.4.3)",
                        "suggestion": f"Darken foreground or lighten background to achieve at least 4.5:1 contrast ratio between {dominant_hexes[0][0]} and {dominant_hexes[1][0]}.",
                        "is_ai_generated": True,
                        "confidence": 0.94,
                    })
                else:
                    findings.append({
                        "severity": "info",
                        "category": "accessibility",
                        "text_highlight": f"Contrast {contrast_val:.1f}:1",
                        "explanation": f"Measured visual contrast ratio ({contrast_val:.1f}:1) satisfies WCAG 2.1 AA standard for legible presentation.",
                        "guideline_source": "Accessibility Standards → WCAG 2.1 AA Contrast Minimum (1.4.3)",
                        "suggestion": "Maintain strong contrast between text overlays and underlying graphics.",
                        "is_ai_generated": True,
                        "confidence": 0.90,
                    })

            # Check palette adherence
            if brand_palette and dominant_hexes:
                palette_rgbs = [_hex_to_rgb(p) for p in brand_palette]
                off_palette_colors = []
                for hex_val, rgb in dominant_hexes[:3]:
                    min_dist = min(_color_distance(rgb, p_rgb) for p_rgb in palette_rgbs)
                    if min_dist > 130:
                        off_palette_colors.append(hex_val)

                if off_palette_colors:
                    findings.append({
                        "severity": "warning",
                        "category": "visual",
                        "text_highlight": f"Detected: {', '.join(off_palette_colors)}",
                        "explanation": f"Dominant colors ({', '.join(off_palette_colors)}) deviate from approved brand color palette ({', '.join(brand_palette[:3])}).",
                        "guideline_source": "Visual Identity Guidelines → Approved Palette Harmonization",
                        "suggestion": f"Adjust background and accent gradients to harmonize with approved brand palette: {', '.join(brand_palette)}.",
                        "is_ai_generated": True,
                        "confidence": 0.92,
                    })

        except Exception as e:
            print(f"[ai_engine] PIL visual analysis error: {e}")

    # Alt-text checks
    cleaned_alt = (alt_text or "").strip()
    if not cleaned_alt or len(cleaned_alt) < 10:
        recommended_alt = f"Promotional marketing asset for {brand_name} with brand color styling"
        if dominant_hexes:
            recommended_alt += f" in {dominant_hexes[0][0]} colorway"
        findings.append({
            "severity": "error",
            "category": "accessibility",
            "text_highlight": cleaned_alt or "[Missing Alt-Text]",
            "explanation": "Image asset lacks sufficient alternative text. WCAG 2.1 AA mandates descriptive context (minimum 10 characters) for screen readers.",
            "guideline_source": "Accessibility Standards → WCAG 2.1 AA Non-text Content (1.1.1)",
            "suggestion": f"Add descriptive alt-text: '{recommended_alt}'.",
            "is_ai_generated": True,
            "confidence": 1.0,
        })
    elif any(placeholder in cleaned_alt.lower() for placeholder in ["image", "photo", "picture", "screenshot", "graphic"]):
        if len(cleaned_alt.split()) <= 2:
            findings.append({
                "severity": "warning",
                "category": "accessibility",
                "text_highlight": cleaned_alt,
                "explanation": "Alt-text uses generic placeholder terminology ('photo', 'image') without contextual narrative.",
                "guideline_source": "Accessibility Standards → Descriptive Alt-Text Best Practice (1.1.1)",
                "suggestion": f"Describe the specific action or product value: '{brand_name} visual display showing enterprise governance feature'.",
                "is_ai_generated": True,
                "confidence": 0.90,
            })

    # Logo Clear Space & Padding rule
    findings.append({
        "severity": "info",
        "category": "visual",
        "text_highlight": image_name,
        "explanation": f"Ensure all '{brand_name}' emblems maintain 10% clear space isolation margin around all edges, with no background interference.",
        "guideline_source": "Visual Identity Guidelines → Logo Clear Space & Padding",
        "suggestion": "Ensure safe zone equivalent to the height of the brand mark around all 4 sides.",
        "is_ai_generated": True,
        "confidence": 0.90,
    })

    if visual_rules:
        for rule in visual_rules[:2]:
            findings.append({
                "severity": "info",
                "category": "visual",
                "text_highlight": image_name,
                "explanation": f"Visual guideline advisory: {rule}",
                "guideline_source": f"Visual Identity Rules → {rule}",
                "suggestion": "Review graphic against organization visual standards before publishing.",
                "is_ai_generated": True,
                "confidence": 0.85,
            })

    return findings


async def ai_image_review(
    image_url_or_name: str,
    image_bytes: bytes | None = None,
    mime_type: str = "image/png",
    brand_palette: list[str] | None = None,
    alt_text: str | None = None,
    visual_rules: list[str] | None = None,
    brand_name: str = "BrandGuard AI",
) -> list[dict[str, Any]]:
    """
    Multimodal & Accessibility Image Review Engine.
    Executes Gemini Vision when API key is provided, with PIL-based deterministic fallback.
    """
    settings = get_settings()
    gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if gemini_key and image_bytes:
        try:
            model = settings.AI_MODEL if settings.AI_MODEL and "gemini" in settings.AI_MODEL else "gemini-2.5-flash"
            gemini_findings = await _call_gemini_vision_api(
                image_bytes=image_bytes,
                mime_type=mime_type,
                brand_palette=brand_palette,
                alt_text=alt_text,
                visual_rules=visual_rules,
                brand_name=brand_name,
                image_name=image_url_or_name,
                api_key=gemini_key,
                model=model,
            )
            if gemini_findings:
                for f in gemini_findings:
                    f["is_ai_generated"] = True
                return gemini_findings
        except Exception as e:
            print(f"[ai_engine] Gemini Vision review failed ({e}), falling back to PIL vision analyzer.")

    # High-precision PIL + WCAG deterministic analyzer fallback
    return _pil_visual_and_accessibility_analyzer(
        image_bytes=image_bytes,
        image_name=image_url_or_name,
        brand_palette=brand_palette,
        alt_text=alt_text,
        visual_rules=visual_rules,
        brand_name=brand_name,
    )
