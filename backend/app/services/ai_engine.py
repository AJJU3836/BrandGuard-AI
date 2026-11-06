"""
BrandGuard AI — AI Review Engine (Stub)

This module will handle LLM-based review grounded in retrieved brand guidelines.

TODO: Full implementation plan:
1. Retrieve relevant guideline chunks from pgvector using the draft content as query
2. Build a grounding prompt that includes the retrieved chunks + tone rules
3. Call the LLM (OpenAI / Gemini) with a system prompt that:
   - Instructs the model to act as a brand compliance reviewer
   - Only cite sources from the provided guideline chunks
   - Return structured findings with severity, explanation, source, and suggestion
   - Flag low-confidence findings as "needs human check"
4. Parse the LLM response into Finding objects
5. For image review: use a vision-capable model to check logo usage, colour consistency
"""

from typing import Any


async def ai_review(
    content: str,
    guideline_chunks: list[str],
    tone_rules: list[str],
    content_type: str = "other",
) -> list[dict[str, Any]]:
    """
    Run AI-powered review of content against brand guidelines.

    Currently returns a placeholder. Will be replaced with full RAG pipeline.

    Args:
        content: The draft text to review.
        guideline_chunks: Retrieved guideline clause texts.
        tone_rules: List of tone rule descriptions.
        content_type: Type of content (social_post, blog, email, ad, other).

    Returns:
        List of finding dicts.
    """
    # TODO: Implement full RAG pipeline:
    # 1. Embed the content → query pgvector for top-K guideline chunks
    # 2. Build grounding prompt with chunks + tone rules
    # 3. Call LLM API
    # 4. Parse structured response into findings
    # 5. Mark low-confidence items

    return [
        {
            "severity": "info",
            "category": "tone",
            "text_highlight": None,
            "explanation": (
                "AI-powered tone, messaging, and claim review will be enabled "
                "once the LLM pipeline is connected. The rule engine checks above "
                "are fully operational."
            ),
            "guideline_source": None,
            "suggestion": None,
            "is_ai_generated": True,
            "confidence": None,
        }
    ]


async def ai_image_review(image_path: str, brand_kit: dict) -> list[dict[str, Any]]:
    """
    Run AI-powered review of an image against brand visual guidelines.

    TODO: Implement with vision-capable model:
    - Check logo placement and colour
    - Verify colour palette usage
    - Check for alt-text (in the metadata context)
    - Assess visual consistency with brand guidelines
    """
    return []
