"""
BrandGuard AI — Brand Kit Service

Handles guideline indexing: splitting text into chunks and storing for retrieval.
Built with zero external C++ dependencies for maximum portability.
"""

import math
import re
from typing import Any
from uuid import UUID
import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.brand_kit import BrandKit
from app.models.guideline_chunk import GuidelineChunk


def compute_embedding(text: str) -> list[float] | None:
    """
    Generate vector embedding using OpenAI or Gemini API if credentials are provided.
    Returns list of floats or None if API keys are absent or request fails.
    """
    settings = get_settings()

    # Try Gemini Embeddings
    gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={gemini_key}"
            payload = {
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": text[:2000]}]},
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("embedding", {}).get("values")
        except Exception as e:
            print(f"[brand_kit_service] Gemini embedding error: {e}")

    # Try OpenAI Embeddings
    if settings.OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/embeddings"
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            payload = {
                "input": text[:2000],
                "model": "text-embedding-3-small",
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["data"][0]["embedding"]
        except Exception as e:
            print(f"[brand_kit_service] OpenAI embedding error: {e}")

    return None


def _tokenize(text: str) -> list[str]:
    """Tokenize and normalize text for lexical ranking."""
    words = re.findall(r"\w+", text.lower())
    stop_words = {
        "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with",
        "is", "are", "was", "were", "it", "this", "that", "these", "those", "we", "our"
    }
    return [w for w in words if len(w) > 2 and w not in stop_words]


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Compute cosine similarity between two vector lists."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


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

    # Store chunks (with optional embeddings if available)
    for i, chunk_text in enumerate(chunks):
        embedding_val = compute_embedding(chunk_text)
        chunk = GuidelineChunk(
            brand_kit_id=brand_kit_id,
            content=chunk_text,
            chunk_index=i,
            source_section=_guess_section(chunk_text),
            embedding=embedding_val,
        )
        db.add(chunk)

    # Mark brand kit as indexed
    brand_kit = db.query(BrandKit).filter(BrandKit.id == brand_kit_id).first()
    if brand_kit:
        brand_kit.is_indexed = True

    db.commit()

    return len(chunks)


def _guess_section(text: str) -> str | None:
    """Try to extract a section heading from the chunk text."""
    lines = text.strip().split("\n")
    first_line = lines[0].strip() if lines else ""
    # If first line looks like a heading (short, possibly numbered)
    if len(first_line) < 80 and (first_line[0].isdigit() or first_line.isupper() or "=" in first_line):
        return first_line.replace("=", "").strip()
    return None


def retrieve_relevant_chunks(
    query: str,
    brand_kit_id: UUID,
    db: Session,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve the most relevant guideline chunks for a draft using hybrid retrieval:
    combines vector embedding cosine similarity with BM25/TF-IDF lexical ranking.
    """
    chunks = (
        db.query(GuidelineChunk)
        .filter(GuidelineChunk.brand_kit_id == brand_kit_id)
        .order_by(GuidelineChunk.chunk_index)
        .all()
    )

    if not chunks:
        return []

    # If there are fewer or equal chunks than top_k, return all
    if len(chunks) <= top_k:
        return [
            {
                "content": c.content,
                "source_section": c.source_section,
                "chunk_index": c.chunk_index,
                "score": 1.0,
            }
            for c in chunks
        ]

    # Compute query embedding for semantic search if possible
    query_emb = compute_embedding(query)
    query_tokens = _tokenize(query)

    # Precompute document frequencies for lexical scoring
    doc_tokens = [_tokenize(c.content) for c in chunks]
    total_docs = len(chunks)
    avg_dl = sum(len(dt) for dt in doc_tokens) / max(1, total_docs)
    df: dict[str, int] = {}
    for dt in doc_tokens:
        for t in set(dt):
            df[t] = df.get(t, 0) + 1

    scored_chunks = []
    for idx, chunk in enumerate(chunks):
        # 1. Lexical BM25 score
        k1 = 1.5
        b = 0.75
        dl = len(doc_tokens[idx])
        bm25_score = 0.0
        for token in query_tokens:
            if token in df:
                # Standard IDF
                idf = math.log((total_docs - df[token] + 0.5) / (df[token] + 0.5) + 1.0)
                tf = doc_tokens[idx].count(token)
                term_score = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avg_dl)))
                bm25_score += term_score

        # Normalize BM25 score approximately
        lexical_score = min(1.0, bm25_score / 15.0) if bm25_score > 0 else 0.0

        # 2. Semantic vector cosine score
        semantic_score = 0.0
        if query_emb and chunk.embedding:
            try:
                semantic_score = max(0.0, _cosine_similarity(query_emb, chunk.embedding))
            except Exception:
                semantic_score = 0.0

        # Hybrid fusion score
        if query_emb and any(c.embedding for c in chunks):
            final_score = 0.6 * semantic_score + 0.4 * lexical_score
        else:
            final_score = lexical_score

        scored_chunks.append({
            "content": chunk.content,
            "source_section": chunk.source_section,
            "chunk_index": chunk.chunk_index,
            "score": final_score,
        })

    # Sort descending by score
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_k]


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
