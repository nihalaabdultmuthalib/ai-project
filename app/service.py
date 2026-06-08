from sqlalchemy.ext.asyncio import AsyncSession

from app.chunking import chunk_text
from app.config import Settings
from app.llm import LLMClient, LocalLLMClient
from app.repository import create_chunks, list_chunks, search_chunks


class QAService:
    def __init__(self, session: AsyncSession, llm: LLMClient | LocalLLMClient, settings: Settings):
        self.session = session
        self.llm = llm
        self.settings = settings

    async def ingest(self, source: str, content: str) -> list[int]:
        chunks = chunk_text(content)
        embedded_chunks = [(chunk, await self.llm.embed(chunk)) for chunk in chunks]
        return await create_chunks(self.session, source, embedded_chunks)

    async def ask(self, question: str) -> tuple[str, list[dict]]:
        question_embedding = await self.llm.embed(question)
        sources = await search_chunks(self.session, question_embedding, self.settings.retrieval_limit)
        context = "\n\n".join(
            f"Source: {source['source']}\nContent: {source['content']}" for source in sources
        )
        answer = await self.llm.answer(question, context)
        return answer, sources

    async def list_documents(self, limit: int = 20) -> list[dict]:
        return await list_chunks(self.session, limit)
