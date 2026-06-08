import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.database import get_session_factory
from app.llm import LLMClient
from app.service import QAService


SAMPLE_DOCUMENT = """
This service is a FastAPI application for question answering over private documents.
It stores document chunks in PostgreSQL with the pgvector extension. At ingestion time,
the service creates OpenAI embeddings for each text chunk. At question time, it embeds
the question, retrieves the most similar document chunks, and asks the chat model to
answer using that context.
"""


async def main() -> None:
    settings = get_settings()
    llm = LLMClient(settings)
    session_factory = get_session_factory()
    async with session_factory() as session:
        service = QAService(session=session, llm=llm, settings=settings)
        ids = await service.ingest("sample-assessment-document.txt", SAMPLE_DOCUMENT)
    print(f"Seeded {len(ids)} chunk(s): {ids}")


if __name__ == "__main__":
    asyncio.run(main())

