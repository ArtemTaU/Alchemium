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
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
