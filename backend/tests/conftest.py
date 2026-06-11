import pytest
from sqlalchemy import text

from app.db.session import AsyncSessionLocal, engine
from app.models.base import Base


@pytest.fixture(scope="session", autouse=True)
async def create_tables():
    """
    Drop and recreate all tables once per test session.
    This is where the UniqueConstraint gets applied to the real database.
    Runs once, not before every test.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
async def clean_tables():
    """
    Wipe all rows after each test so tests don't share state.
    'yield' means: run the test first, then run the cleanup below it.
    TRUNCATE is much faster than DROP/CREATE for isolation between tests.
    """
    yield
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("TRUNCATE TABLE records, data_sources RESTART IDENTITY CASCADE")
        )
        await session.commit()