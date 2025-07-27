import pytest
import sqlalchemy
from src.exceptions import DataValidationError
from src.uow import UnitOfWork
from tests.models import User, UserRepository


@pytest.mark.asyncio
async def test_update_user_success(async_session_factory):
    """
    Test successful update of a user instance.
    """
    initial_name = "Initial"
    update_data = {"name": "UpdatedName"}

    async with UnitOfWork(async_session_factory) as uow:
        user = User(name=initial_name)
        uow.session.add(user)

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == initial_name)
        )
        user = result.scalar_one()
        UserRepository.update(user, update_data)

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
    initial_name = "Initial"
    update_data = {"nonexistent_field": "value"}

    async with UnitOfWork(async_session_factory) as uow:
        user = User(name=initial_name)
        uow.session.add(user)

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == initial_name)
        )
        user = result.scalar_one()
        with pytest.raises(DataValidationError):
            UserRepository.update(user, update_data)
