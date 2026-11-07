"""
BrandGuard AI — Unit & Integration Test for Core AI Engine & Semantic Retrieval
"""

import asyncio
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from uuid import uuid4
from app.services.ai_engine import ai_review, ai_image_review
from app.services.brand_kit_service import split_text, _tokenize, _cosine_similarity


async def test_ai_tone_and_claim_checks():
    print("\n--- Testing AI Tone & Claim Checks ---")
    draft_content = (
        "BUY NOW! Our revolutionary tool has 99.9% market dominance and unbelievable speed!! "
        "Yo, gonna make your workflow hella fast with zero downtime."
    )
    tone_rules = [
        "Tone: Professional, Empathetic, Objective, Authoritative, Clear.",
        "Avoid: Hyperbole, excessive emojis, sensationalism, aggressive sales pressure.",
    ]
    approved_facts = [
        "Over 500+ enterprise clients onboarded",
        "Founded in 2024",
        "ASCI pre-publication guideline compliant",
    ]
    guideline_chunks = [
        {
            "content": "BrandGuard AI operates with enterprise authority. Avoid hyperbole.",
            "source_section": "1. BRAND MISSION & VOICE",
        }
    ]

    findings = await ai_review(
        content=draft_content,
        guideline_chunks=guideline_chunks,
        tone_rules=tone_rules,
        approved_facts=approved_facts,
        content_type="social_post",
    )

    print(f"Detected {len(findings)} AI findings:")
    for f in findings:
        print(f"  • [{f['severity'].upper()}] {f['category']}: \"{f.get('text_highlight')}\"")
        print(f"    Reason: {f['explanation']}")
        print(f"    Source: {f['guideline_source']}")
        print(f"    Suggestion: {f['suggestion']}\n")

    assert len(findings) >= 3, f"Expected at least 3 findings, got {len(findings)}"
    categories = {f["category"] for f in findings}
    assert "tone" in categories, "Expected 'tone' category in findings"
    assert "claim" in categories, "Expected 'claim' category in findings"
    print("✓ AI Tone & Claim Engine verified successfully!")


async def test_ai_image_accessibility():
    print("\n--- Testing AI Image Accessibility & Visual Review ---")
    # Test missing alt-text
    findings_no_alt = await ai_image_review(
        image_url_or_name="banner_promo.png",
        brand_palette=["#1E40AF", "#2563EB"],
        alt_text="",
        visual_rules=["Primary logo requires 10% clear space padding."],
    )
    print(f"Image findings count: {len(findings_no_alt)}")
    assert any(f["category"] == "accessibility" for f in findings_no_alt), "Expected accessibility flag for missing alt-text"
    print("✓ Image Accessibility checks verified successfully!")


def test_text_splitting_and_retrieval():
    print("\n--- Testing Text Splitting & Tokenizer ---")
    sample_text = (
        "SECTION 1: MISSION\n\n"
        "BrandGuard AI protects organisations from brand degradation.\n\n"
        "SECTION 2: RULES\n\n"
        "Never use unapproved claims or offensive language."
    )
    chunks = split_text(sample_text, chunk_size=100)
    assert len(chunks) >= 2, "Expected multiple chunks"
    tokens = _tokenize("BrandGuard AI protects our company!")
    assert "brandguard" in tokens
    assert "protects" in tokens
    assert "our" not in tokens  # Stop word removed
    print("✓ Text splitting & tokenizer verified successfully!")


if __name__ == "__main__":
    test_text_splitting_and_retrieval()
    asyncio.run(test_ai_tone_and_claim_checks())
    asyncio.run(test_ai_image_accessibility())
    print("\n🎉 ALL AI & BACKEND ENGINE TESTS PASSED!")
