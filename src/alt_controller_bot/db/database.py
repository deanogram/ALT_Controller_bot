from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from alt_controller_bot.core.config import settings


def build_engine(echo: bool = False) -> AsyncEngine:
    return create_async_engine(str(settings.database_url), echo=echo, future=True)


def build_session_factory(engine: AsyncEngine | None = None) -> async_sessionmaker[AsyncSession]:
    engine = engine or build_engine()
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


engine = build_engine()
async_session_factory = build_session_factory(engine)


@asynccontextmanager
async def session_scope():
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
