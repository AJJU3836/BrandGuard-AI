"""
BrandGuard AI — Deterministic Rule Engine

Checks content against brand kit rules without any AI.
Runs BEFORE the AI engine — fast, reliable, explainable.
"""

import re
from typing import Any


def check_banned_terms(content: str, banned_terms: list[str]) -> list[dict[str, Any]]:
    """
    Check if content contains any banned terminology.

    Returns a list of findings for each banned term found.
    """
    findings = []
    content_lower = content.lower()

    for term in banned_terms:
        term_lower = term.lower()
        # Use word-boundary matching so "cheap" doesn't match "cheapskate" false-positively
        pattern = re.compile(r'\b' + re.escape(term_lower) + r'\b', re.IGNORECASE)
        matches = list(pattern.finditer(content))

        for match in matches:
            # Extract surrounding context (up to 40 chars each side)
            start = max(0, match.start() - 40)
            end = min(len(content), match.end() + 40)
            context = content[start:end]

            findings.append({
                "severity": "error",
                "category": "terminology",
                "text_highlight": match.group(),
                "explanation": (
                    f'The term "{match.group()}" is on the banned terminology list. '
                    f"It should not appear in any brand content."
                ),
                "guideline_source": f"Banned Terms List → \"{term}\"",
                "suggestion": f'Remove or replace "{match.group()}" with an approved alternative.',
                "is_ai_generated": False,
                "confidence": 1.0,
            })

    return findings


def check_approved_terms(content: str, approved_terms: list[str]) -> list[dict[str, Any]]:
    """
    Check for common variant misspellings of approved terms.

    For example, if "BrandGuard" is approved, flag "Brand Guard" or "brandguard".
    """
    findings = []
    if not approved_terms:
        return findings

    for term in approved_terms:
        # Build variants: lowercase, split with spaces, joined without spaces
        term_stripped = term.strip()
        if not term_stripped:
            continue

        # Check if the exact approved term is present (good — skip)
        if term_stripped in content:
            continue

        # Check for case-insensitive match (wrong casing)
        pattern = re.compile(re.escape(term_stripped), re.IGNORECASE)
        matches = list(pattern.finditer(content))

        for match in matches:
            if match.group() != term_stripped:  # Different casing
                findings.append({
                    "severity": "warning",
                    "category": "terminology",
                    "text_highlight": match.group(),
                    "explanation": (
                        f'The term "{match.group()}" appears to be a variant of the '
                        f'approved term "{term_stripped}". Use the exact approved spelling.'
                    ),
                    "guideline_source": f"Approved Terms List → \"{term_stripped}\"",
                    "suggestion": f'Replace "{match.group()}" with "{term_stripped}".',
                    "is_ai_generated": False,
                    "confidence": 0.9,
                })

    return findings


def check_unsupported_claims(content: str, approved_facts: list[str]) -> list[dict[str, Any]]:
    """
    Flag promotional claims that are NOT in the approved facts list.

    Catches superlatives and absolute claims like "#1", "best", "100%",
    "guaranteed", "world-class", etc.
    """
    findings = []
    approved_lower = [f.lower() for f in approved_facts]

    # Patterns for promotional / absolute claims
    claim_patterns = [
        (r'#\s*1\b', "\"#1\" ranking claim"),
        (r'\b100\s*%\b', "\"100%\" absolute claim"),
        (r'\bbest\b', "\"best\" superlative claim"),
        (r'\bguarantee[ds]?\b', "guarantee claim"),
        (r'\bworld[\s-]?class\b', "\"world-class\" claim"),
        (r'\bindustry[\s-]?leading\b', "\"industry-leading\" claim"),
        (r'\bno[\s-]?risk\b', "\"no risk\" claim"),
        (r'\brisk[\s-]?free\b', "\"risk-free\" claim"),
        (r'\bfirst[\s-]?ever\b', "\"first-ever\" claim"),
        (r'\bonly\s+(?:one|company|product|solution)\b', "exclusivity claim"),
        (r'\bproven\b', "\"proven\" claim"),
        (r'\bclinically\s+(?:proven|tested)\b', "clinical claim"),
        (r'\bscientifically\s+(?:proven|tested)\b', "scientific claim"),
        (r'\bunbeatable\b', "\"unbeatable\" claim"),
        (r'\bsuperior\b', "\"superior\" claim"),
        (r'\bunmatched\b', "\"unmatched\" claim"),
        (r'\bmost\s+(?:advanced|powerful|trusted|popular|effective)\b', "superlative claim"),
    ]

    for pattern_str, claim_desc in claim_patterns:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        matches = list(pattern.finditer(content))

        for match in matches:
            matched_text = match.group()

            # Check if this claim is in the approved facts
            is_approved = any(
                matched_text.lower() in fact for fact in approved_lower
            )
            if is_approved:
                continue

            # Extract context
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].strip()

            findings.append({
                "severity": "warning",
                "category": "claim",
                "text_highlight": context,
                "explanation": (
                    f"Detected a {claim_desc}: \"{matched_text}\". "
                    f"This claim is not in the approved facts list. "
                    f"Unsupported promotional claims can carry legal risk (ASCI guidelines)."
                ),
                "guideline_source": "Approved Facts List — claim not found",
                "suggestion": (
                    f"Either add supporting evidence to the approved facts list, "
                    f"or rephrase to remove the unsupported claim."
                ),
                "is_ai_generated": False,
                "confidence": 0.85,
            })

    return findings


def check_color_palette(content: str, approved_colors: list[str]) -> list[dict[str, Any]]:
    """
    Check for hex colour codes in content that aren't in the approved palette.

    Useful for catching off-brand colours in HTML/CSS content, email templates, etc.
    """
    findings = []
    if not approved_colors:
        return findings

    approved_hex = {c.lower().strip() for c in approved_colors}

    # Find hex colour codes
    hex_pattern = re.compile(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')
    matches = list(hex_pattern.finditer(content))

    for match in matches:
        color = match.group().lower()
        if color not in approved_hex:
            findings.append({
                "severity": "warning",
                "category": "visual",
                "text_highlight": match.group(),
                "explanation": (
                    f"Colour {match.group()} is not in the approved brand palette. "
                    f"Approved colours: {', '.join(approved_colors)}."
                ),
                "guideline_source": f"Brand Colour Palette → approved: {', '.join(approved_colors)}",
                "suggestion": f"Replace {match.group()} with an approved brand colour.",
                "is_ai_generated": False,
                "confidence": 1.0,
            })

    return findings


def run_all_checks(
    content: str,
    banned_terms: list[str] | None = None,
    approved_terms: list[str] | None = None,
    approved_facts: list[str] | None = None,
    color_palette: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Run all deterministic rule checks and return combined findings.

    This is the main entry point for the rule engine.
    """
    all_findings = []

    if banned_terms:
        all_findings.extend(check_banned_terms(content, banned_terms))

    if approved_terms:
        all_findings.extend(check_approved_terms(content, approved_terms))

    if approved_facts is not None:  # Run even with empty list to catch unsupported claims
        all_findings.extend(check_unsupported_claims(content, approved_facts))

    if color_palette:
        all_findings.extend(check_color_palette(content, color_palette))

    return all_findings
