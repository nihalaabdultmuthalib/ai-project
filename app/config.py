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
    gemini_api_key: str | None = None
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ai_qa"
    retrieval_limit: int = 5


@lru_cache
def get_settings() -> Settings:
    _load_dotenv()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Defaults adjust dynamically based on if Gemini is used
    default_chat = "gemini-2.5-flash" if gemini_api_key else "gpt-4o-mini"
    default_embed = "gemini-embedding-001" if gemini_api_key else "text-embedding-3-small"
    default_dim = 768 if gemini_api_key else 1536
    
    return Settings(
        app_name=os.getenv("APP_NAME", "AI QA Service"),
        environment=os.getenv("ENVIRONMENT", "development"),
        use_local_ai=os.getenv("USE_LOCAL_AI", "false").lower() in {"1", "true", "yes", "on"},
        openai_api_key=openai_api_key,
        gemini_api_key=gemini_api_key,
        openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", default_chat),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", default_embed),
        embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", str(default_dim))),
        database_url=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_qa"),
        retrieval_limit=int(os.getenv("RETRIEVAL_LIMIT", "5")),
    )
