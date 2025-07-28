"""
File: conftest.py

This file defines the main fixtures for asynchronous database work in tests (Alchemium).
The `async_engine` and `async_session` fixtures are required for any test interacting with the database.

--------------------------
Pytest automatically discovers all fixtures only from files named `conftest.py` in your project.
If you place your fixtures here, they will be available in all tests without manual import.
This is the standard practice for all shared fixtures.

Example usage:
--------------
Simply specify the fixture as an argument in your test:
    async def test_example(async_session):
        # your test code

IMPORTANT:
- The DATABASE_URL should point to a dedicated test database or use in-memory SQLite.
"""

from unittest.mock import AsyncMock

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from .models import Base

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_engine():
    """
    Provides an asynchronous SQLAlchemy engine for the test database.

    Yields:
        AsyncEngine: An async SQLAlchemy engine instance.

    The engine is created for the duration of the test and disposed of after use.
    """
    engine = create_async_engine(DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    """
    Provides an asynchronous SQLAlchemy session for the test database,
    with all tables created before yielding.

    Args:
        async_engine (AsyncEngine): The async engine fixture.

    Yields:
        AsyncSession: An async SQLAlchemy session for database operations.

    The session is created using an in-memory SQLite database for test isolation.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_session_factory(async_engine):
    """
    Provides a factory for creating asynchronous SQLAlchemy sessions
    for the test database.

    Args:
        async_engine (AsyncEngine): The async engine fixture.

    Yields:
        Callable[..., AsyncSession]: A factory function to create new async sessions.

    The factory can be used to create multiple independent sessions within one test,
    ensuring test isolation when needed. All tables are created before yielding the factory.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
def mock_session():
    """
    Provides a mock asynchronous SQLAlchemy session for unit tests.

    Yields:
        AsyncMock: A mock AsyncSession object.

    Useful for testing repository logic without a real database.
    Can be used to assert calls and control the return values of session methods.

    Example usage:
        def test_service_logic(mock_session):
            # mock_session can be configured here
            ...
    """
    session = AsyncMock()
    return session
