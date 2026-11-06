"""
BrandGuard AI — Brand Kit Service

Handles guideline indexing: splitting text into chunks and storing for retrieval.
"""

from uuid import UUID

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from app.models.brand_kit import BrandKit
from app.models.guideline_chunk import GuidelineChunk


def index_guidelines(brand_kit_id: UUID, guidelines_text: str, db: Session) -> int:
    """
    Split guidelines text into chunks and store them for retrieval.

    Args:
        brand_kit_id: The brand kit to index.
        guidelines_text: Raw guideline text to split.
        db: Database session.

    Returns:
        Number of chunks created.
    """
    # Delete existing chunks for this brand kit
    db.query(GuidelineChunk).filter(
        GuidelineChunk.brand_kit_id == brand_kit_id
    ).delete()

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_text(guidelines_text)

    # Store chunks
    for i, chunk_text in enumerate(chunks):
        chunk = GuidelineChunk(
            brand_kit_id=brand_kit_id,
            content=chunk_text,
            chunk_index=i,
            source_section=_guess_section(chunk_text),
        )
        db.add(chunk)

    # Mark brand kit as indexed
    brand_kit = db.query(BrandKit).filter(BrandKit.id == brand_kit_id).first()
    if brand_kit:
        brand_kit.is_indexed = True

    db.commit()

    # TODO: Generate embeddings for each chunk using OpenAI/Gemini embeddings API
    # and store them in the `embedding` column for vector search.

    return len(chunks)


def _guess_section(text: str) -> str | None:
    """Try to extract a section heading from the chunk text."""
    lines = text.strip().split("\n")
    first_line = lines[0].strip() if lines else ""
    # If first line looks like a heading (short, possibly numbered)
    if len(first_line) < 80 and (first_line[0].isdigit() or first_line.isupper()):
        return first_line
    return None


def get_guideline_chunks(brand_kit_id: UUID, db: Session) -> list[str]:
    """
    Retrieve all guideline chunk texts for a brand kit.

    TODO: Replace with vector similarity search once embeddings are generated.
    For now, returns all chunks (brute-force retrieval).
    """
    chunks = (
        db.query(GuidelineChunk)
        .filter(GuidelineChunk.brand_kit_id == brand_kit_id)
        .order_by(GuidelineChunk.chunk_index)
        .all()
    )
    return [c.content for c in chunks]
