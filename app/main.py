import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_session
from app.llm import LLMClient, LLMError, LocalLLMClient
from app.schemas import (
    AnswerResponse,
    DocumentChunkResponse,
    HealthResponse,
    IngestRequest,
    IngestResponse,
    QuestionRequest,
    RootResponse,
)
from app.service import QAService

app = FastAPI(
    title="AI QA Service",
    description="FastAPI service with OpenAI question answering and PostgreSQL/pgvector retrieval.",
    version="1.0.0",
)


def get_llm(settings: Settings = Depends(get_settings)) -> LLMClient | LocalLLMClient:
    if settings.use_local_ai:
        return LocalLLMClient(settings)

    try:
        return LLMClient(settings)
    except LLMError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


def get_qa_service(
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
    llm: LLMClient = Depends(get_llm),
) -> QAService:
    return QAService(session=session, llm=llm, settings=settings)


@app.get("/", response_model=RootResponse)
async def home(settings: Settings = Depends(get_settings)) -> RootResponse:
    return RootResponse(
        name=settings.app_name,
        status="ok",
        docs_url="/docs",
        health_url="/health",
    )


@app.get("/health", response_model=HealthResponse)
async def health(session: AsyncSession = Depends(get_session)) -> HealthResponse:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable.",
        ) from exc
    return HealthResponse(status="ok")


@app.post("/documents", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    payload: IngestRequest,
    qa_service: QAService = Depends(get_qa_service),
) -> IngestResponse:
    try:
        chunk_ids = await qa_service.ingest(payload.source, payload.content)
    except (LLMError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return IngestResponse(ids=chunk_ids, source=payload.source)


@app.get("/documents", response_model=list[DocumentChunkResponse])
async def get_documents(
    limit: int = 20,
    qa_service: QAService = Depends(get_qa_service),
) -> list[DocumentChunkResponse]:
    try:
        rows = await qa_service.list_documents(limit=limit)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not list documents.") from exc

    return [
        DocumentChunkResponse(
            id=row["id"],
            source=row["source"],
            content=row["content"],
            created_at=str(row.get("created_at")) if row.get("created_at") else None,
        )
        for row in rows
    ]


@app.post("/ask", response_model=AnswerResponse)
async def ask(
    payload: QuestionRequest,
    qa_service: QAService = Depends(get_qa_service),
) -> AnswerResponse:
    try:
        answer, sources = await qa_service.ask(payload.question)
    except (LLMError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return AnswerResponse(answer=answer, sources=sources)
