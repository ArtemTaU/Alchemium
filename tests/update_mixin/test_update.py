import pytest
from unittest.mock import patch, AsyncMock

import sqlalchemy
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError

from src.exceptions import (
    DataValidationError,
    TransactionError,
    UnknownTransactionError,
    ForeignKeyViolation,
    UniqueViolation,
)
from src.uow import UnitOfWork
from tests.models import UserRepository, User


@pytest.mark.asyncio
async def test_update_user_success(async_session_factory):
    """
    Test successful update of a user instance.
    """
    original_name = "OriginalName"
    update_data = {"name": "UpdatedName"}

    async with UnitOfWork(async_session_factory) as uow:
        user = User(name=original_name)
        uow.session.add(user)

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == original_name)
        )
        user = result.scalar_one()
        await UserRepository.update(uow.session, user, update_data)
        await uow.commit()

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == "UpdatedName")
        )
        updated_user = result.scalar_one()
        assert updated_user.name == "UpdatedName"


@pytest.mark.asyncio
async def test_update_invalid_field_raises_data_validation_error(async_session_factory):
    """
    Test that updating with an invalid field raises DataValidationError.
    """
    initial_data = {"name": "Initial"}
    update_data = {"nonexistent_field": "value"}

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.create(uow.session, initial_data)
        await uow.commit()

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == "Initial")
        )
        user = result.scalar_one()
        with pytest.raises(DataValidationError):
            await UserRepository.update(uow.session, user, update_data)


@pytest.mark.asyncio
async def test_update_unique_violation(async_session_factory):
    """
    Test that UniqueViolation is raised on unique constraint conflict.
    """
    user1 = {"name": "UserA"}
    user2 = {"name": "UserB"}

    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user1)
        await UserRepository.create(uow.session, user2)
        await uow.commit()

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == "UserB")
        )
        user_b = result.scalar_one()

        user_b.name = "UserA"  # simulate unique conflict
        with patch.object(
            uow.session,
            "commit",
            AsyncMock(
                side_effect=IntegrityError("unique", None, "UNIQUE constraint failed")
            ),
        ):
            with pytest.raises(UniqueViolation):
                await uow.commit()


@pytest.mark.asyncio
async def test_update_foreign_key_violation(async_session_factory):
    """
    Test that ForeignKeyViolation is raised on FK constraint failure.
    """
    user_data = {"name": "Someone"}

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.create(uow.session, user_data)
        await uow.commit()

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == "Someone")
        )
        user = result.scalar_one()

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
                await UserRepository.update(uow.session, user, {"name": "Another"})
                await uow.commit()


@pytest.mark.asyncio
async def test_update_data_validation_error(async_session_factory):
    """
    Test that DataValidationError is raised on invalid data during DB commit.
    """
    user_data = {"name": "Name"}

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.create(uow.session, user_data)
        await uow.commit()

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == "Name")
        )
        user = result.scalar_one()

        with patch.object(
            uow.session,
            "commit",
            AsyncMock(side_effect=DataError("bad data", None, None)),
        ):
            with pytest.raises(DataValidationError):
                await UserRepository.update(uow.session, user, {"name": "Invalid"})
                await uow.commit()


@pytest.mark.asyncio
async def test_update_transaction_error(async_session_factory):
    """
    Test that TransactionError is raised on SQLAlchemyError.
    """
    user_data = {"name": "User"}

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.create(uow.session, user_data)
        await uow.commit()

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == "User")
        )
        user = result.scalar_one()

        with patch.object(
            uow.session,
            "commit",
            AsyncMock(side_effect=SQLAlchemyError("some db issue")),
        ):
            with pytest.raises(TransactionError):
                await UserRepository.update(uow.session, user, {"name": "Another"})
                await uow.commit()


@pytest.mark.asyncio
async def test_update_unknown_transaction_error(async_session_factory):
    """
    Test that UnknownTransactionError is raised on unexpected error.
    """
    user_data = {"name": "Someone"}

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.create(uow.session, user_data)
        await uow.commit()

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == "Someone")
        )
        user = result.scalar_one()

        with patch.object(
            uow.session,
            "commit",
            AsyncMock(side_effect=RuntimeError("unexpected")),
        ):
            with pytest.raises(UnknownTransactionError):
                await UserRepository.update(uow.session, user, {"name": "Another"})
                await uow.commit()
