"""
Integration tests for Create Mixin and custom exception handling.

This module tests that Create Mixin correctly creates db objects and raises the expected custom
exceptions on various SQLAlchemy errors (unique violation, foreign key violation,
data errors, transaction errors, and unknown errors). Most error cases are simulated
via mocking since some database constraint violations may not occur with in-memory
SQLite databases.

Fixtures:
    async_session (AsyncSession): Provided by test configuration, represents an async DB session.

Tested exceptions:
    - UniqueViolation
    - ForeignKeyViolation
    - DataValidationError
    - TransactionError
    - CreateError
    - UnknownCreateError
"""

from unittest.mock import patch, AsyncMock

import pytest
import sqlalchemy
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError
from alchemium.errors import (
    UniqueViolation,
    ForeignKeyViolation,
    DataValidationError,
    TransactionError,
    UnknownTransactionError,
)
from alchemium import UnitOfWork
from tests.models import UserRepository, User


@pytest.mark.asyncio
async def test_create_user(async_session_factory):
    """
    Test that a new user can be created and retrieved from the database using UnitOfWork.

    This test verifies that the `UserRepository.create` method correctly adds
    a new user to the database within a UoW transaction, and that the user can
    be subsequently queried using SQLAlchemy ORM queries.

    Steps:
        1. Create a new user instance via the repository inside UoW.
        2. Commit the transaction via UoW (automatically on exit).
        3. Retrieve the user by name from the database.
        4. Assert that the retrieved user has the expected name.

    Args:
        async_session_factory (async_sessionmaker): Fixture providing session factory for UoW.

    Raises:
        AssertionError: If the user retrieved from the database does not have the expected name.
    """
    user_data = {"name": "Alchemium"}

    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == "Alchemium")
        )
        user = result.scalar_one()
        assert user.name == "Alchemium"


@pytest.mark.asyncio
async def test_create_unique_violation(async_session_factory):
    """
    Test that UniqueViolation is raised when a unique constraint is violated.

    This test creates a user, then attempts to create another user with the same unique field.
    It asserts that the custom UniqueViolation exception is raised.
    """
    user_data = {"name": "Alchemium"}

    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    with pytest.raises(UniqueViolation):
        async with UnitOfWork(async_session_factory) as uow:
            await UserRepository.create(uow.session, user_data)


@pytest.mark.asyncio
async def test_create_foreign_key_violation(async_session_factory):
    """
    Test that ForeignKeyViolation is raised when a foreign key constraint is violated.

    This test uses mocking to simulate an IntegrityError caused by a foreign key violation.
    """
    user_data = {"name": "Alchemium"}

    async with UnitOfWork(async_session_factory) as uow:
        with patch.object(
            uow.session,
            "commit",
            AsyncMock(
                side_effect=IntegrityError(
                    "foreign key", None, "FOREIGN KEY constraint failed"
                )
            ),
        ):
            with pytest.raises(ForeignKeyViolation):
                await UserRepository.create(uow.session, user_data)
                await uow.commit()


@pytest.mark.asyncio
async def test_create_data_validation_error(async_session_factory):
    """
    Test that DataValidationError is raised when a DataError occurs.

    This test uses mocking to simulate a DataError during commit.
    """
    user_data = {"name": "Alchemium"}

    async with UnitOfWork(async_session_factory) as uow:
        with patch.object(
            uow.session,
            "commit",
            AsyncMock(side_effect=DataError("bad data", None, None)),
        ):
            with pytest.raises(DataValidationError):
                await UserRepository.create(uow.session, user_data)
                await uow.commit()


@pytest.mark.asyncio
async def test_create_transaction_error(async_session_factory):
    """
    Test that TransactionError is raised on a general SQLAlchemyError.

    This test uses mocking to simulate a SQLAlchemyError during commit.
    """
    user_data = {"name": "Alchemium"}

    async with UnitOfWork(async_session_factory) as uow:
        with patch.object(
            uow.session, "commit", AsyncMock(side_effect=SQLAlchemyError("db error"))
        ):
            with pytest.raises(TransactionError):
                await UserRepository.create(uow.session, user_data)
                await uow.commit()


@pytest.mark.asyncio
async def test_create_unknown_create_error(async_session_factory):
    """
    Test that UnknownCreateError is raised on an unexpected (non-SQLAlchemy) exception.

    This test uses mocking to simulate an unknown error during commit.
    """
    user_data = {"name": "Alchemium"}

    async with UnitOfWork(async_session_factory) as uow:
        with patch.object(
            uow.session, "commit", AsyncMock(side_effect=RuntimeError("unexpected"))
        ):
            with pytest.raises(UnknownTransactionError):
                await UserRepository.create(uow.session, user_data)
                await uow.commit()


@pytest.mark.asyncio
async def test_create_generic_integrity_error(async_session_factory):
    """
    Test that CreateError is raised on a generic IntegrityError not classified as unique or foreign key.

    This test uses mocking to simulate a generic IntegrityError (e.g., check constraint).
    """
    user_data = {"name": "Alchemium"}

    async with UnitOfWork(async_session_factory) as uow:
        with patch.object(
            uow.session,
            "commit",
            AsyncMock(side_effect=IntegrityError("check constraint", None, None)),
        ):
            with pytest.raises(DataValidationError):
                await UserRepository.create(uow.session, user_data)
                await uow.commit()
