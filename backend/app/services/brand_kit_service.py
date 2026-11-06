"""
BrandGuard AI — Brand Kit Service

Handles guideline indexing: splitting text into chunks and storing for retrieval.
Built with zero external C++ dependencies for maximum portability.
"""

from uuid import UUID
from sqlalchemy.orm import Session

from app.models.brand_kit import BrandKit
from app.models.guideline_chunk import GuidelineChunk


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """
    Splits text into coherent chunks by paragraphs and sentences.
    Zero-dependency pure Python replacement for RecursiveCharacterTextSplitter.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        if len(current_chunk) + len(p) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{p}" if current_chunk else p
        else:
            if current_chunk:
                chunks.append(current_chunk)

            # If paragraph itself exceeds chunk_size, split by lines/sentences
            if len(p) > chunk_size:
                lines = p.split("\n")
                sub_chunk = ""
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if len(sub_chunk) + len(line) + 1 <= chunk_size:
                        sub_chunk = f"{sub_chunk}\n{line}" if sub_chunk else line
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = line
                if sub_chunk:
                    chunks.append(sub_chunk)
                current_chunk = ""
            else:
                current_chunk = p

    if current_chunk:
        chunks.append(current_chunk)

    return chunks if chunks else [text]


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
    chunks = split_text(guidelines_text, chunk_size=500, chunk_overlap=50)

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
    if len(first_line) < 80 and (first_line[0].isdigit() or first_line.isupper() or "=" in first_line):
        return first_line.replace("=", "").strip()
    return None


def get_guideline_chunks(brand_kit_id: UUID, db: Session) -> list[str]:
    """
    Retrieve all guideline chunk texts for a brand kit.
    """
    chunks = (
        db.query(GuidelineChunk)
        .filter(GuidelineChunk.brand_kit_id == brand_kit_id)
        .order_by(GuidelineChunk.chunk_index)
        .all()
    )
    return [c.content for c in chunks]
