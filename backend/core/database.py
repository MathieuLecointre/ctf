from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.core.config import settings

# Creation du moteur asynchrone SQLAlchemy
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# Fabrique de sessions asynchrones
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Classe de base pour tous les modeles SQLAlchemy."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependance FastAPI fournissant une session de base de donnees asynchrone.
    Garantit la fermeture propre de la session apres chaque requete HTTP.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
