import json
import math

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def create_chunk(session: AsyncSession, source: str, content: str, embedding: list[float]) -> int:
    result = await session.execute(
        text(
            """
            INSERT INTO document_chunks (source, content, embedding)
            VALUES (:source, :content, CAST(:embedding AS jsonb))
            RETURNING id
            """
        ),
        {"source": source, "content": content, "embedding": json.dumps(embedding)},
    )
    await session.commit()
    return int(result.scalar_one())


async def create_chunks(session: AsyncSession, source: str, chunks: list[tuple[str, list[float]]]) -> list[int]:
    ids: list[int] = []
    for content, embedding in chunks:
        result = await session.execute(
            text(
                """
                INSERT INTO document_chunks (source, content, embedding)
                VALUES (:source, :content, CAST(:embedding AS jsonb))
                RETURNING id
                """
            ),
            {"source": source, "content": content, "embedding": json.dumps(embedding)},
        )
        ids.append(int(result.scalar_one()))
    await session.commit()
    return ids


async def search_chunks(session: AsyncSession, embedding: list[float], limit: int) -> list[dict]:
    # Fetch all rows and compute cosine similarity in Python (no pgvector needed)
    result = await session.execute(
        text("SELECT id, source, content, embedding FROM document_chunks")
    )
    rows = result.fetchall()

    scored = []
    for row in rows:
        stored = json.loads(row.embedding) if isinstance(row.embedding, str) else row.embedding
        score = _cosine_similarity(embedding, stored)
        scored.append({"id": row.id, "source": row.source, "content": row.content, "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


async def list_chunks(session: AsyncSession, limit: int) -> list[dict]:
    result = await session.execute(
        text(
            """
            SELECT id, source, content, created_at
            FROM document_chunks
            ORDER BY created_at DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    )

    return [
        {
            "id": row.id,
            "source": row.source,
            "content": row.content,
            "created_at": row.created_at,
        }
        for row in result
    ]
