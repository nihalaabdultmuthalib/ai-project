from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

SessionFactory = async_sessionmaker[AsyncSession]
_session_factory: SessionFactory | None = None


def _async_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def get_session_factory() -> SessionFactory:
    global _session_factory
    if _session_factory is None:
        settings = get_settings()
        engine = create_async_engine(_async_database_url(settings.database_url), pool_pre_ping=True)
        _session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_factory()() as session:
        yield session
