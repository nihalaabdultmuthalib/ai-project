from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    name: str
    status: str
    docs_url: str
    health_url: str


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["What does this service do?"])


class Source(BaseModel):
    id: int
    source: str
    content: str
    score: float


class AnswerResponse(BaseModel):
    answer: str
    sources: list[Source]


class IngestRequest(BaseModel):
    source: str = Field(..., min_length=1, examples=["company-handbook.md"])
    content: str = Field(..., min_length=20)


class IngestResponse(BaseModel):
    ids: list[int]
    source: str


class DocumentChunkResponse(BaseModel):
    id: int
    source: str
    content: str
    created_at: str | None = None


class HealthResponse(BaseModel):
    status: str
