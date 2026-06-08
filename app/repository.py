from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_chunk(session: AsyncSession, source: str, content: str, embedding: list[float]) -> int:
    result = await session.execute(
        text(
            """
            INSERT INTO document_chunks (source, content, embedding)
            VALUES (:source, :content, CAST(:embedding AS vector))
            RETURNING id
            """
        ),
        {"source": source, "content": content, "embedding": str(embedding)},
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
                VALUES (:source, :content, CAST(:embedding AS vector))
                RETURNING id
                """
            ),
            {"source": source, "content": content, "embedding": str(embedding)},
        )
        ids.append(int(result.scalar_one()))
    await session.commit()
    return ids


async def search_chunks(session: AsyncSession, embedding: list[float], limit: int) -> list[dict]:
    result = await session.execute(
        text(
            """
            SELECT id, source, content, 1 - (embedding <=> CAST(:embedding AS vector)) AS score
            FROM document_chunks
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """
        ),
        {"embedding": str(embedding), "limit": limit},
    )

    return [
        {"id": row.id, "source": row.source, "content": row.content, "score": float(row.score)}
        for row in result
    ]


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
