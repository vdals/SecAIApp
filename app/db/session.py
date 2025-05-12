from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.config import settings

engine = create_async_engine(str(settings.DATABASE_URL), echo=settings.DEBUG, future=True)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False, 
    autocommit=False, 
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting a database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Export all models for Alembic
from app.auth.models import *  # noqa
from app.users.models import *  # noqa
from app.locations.models import *  # noqa
from app.cameras.models import *  # noqa
from app.videos.models import *  # noqa
from app.events.models import *  # noqa 