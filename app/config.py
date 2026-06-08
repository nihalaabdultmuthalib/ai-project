import os
from dataclasses import dataclass
from functools import lru_cache


def _load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI QA Service"
    environment: str = "development"
    use_local_ai: bool = False
    openai_api_key: str | None = None
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ai_qa"
    retrieval_limit: int = 5


@lru_cache
def get_settings() -> Settings:
    _load_dotenv()
    return Settings(
        app_name=os.getenv("APP_NAME", "AI QA Service"),
        environment=os.getenv("ENVIRONMENT", "development"),
        use_local_ai=os.getenv("USE_LOCAL_AI", "false").lower() in {"1", "true", "yes", "on"},
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
        database_url=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_qa"),
        retrieval_limit=int(os.getenv("RETRIEVAL_LIMIT", "5")),
    )
