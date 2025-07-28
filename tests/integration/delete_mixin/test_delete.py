import pytest
import sqlalchemy
from src.exceptions import RepositoryUsageError
from src.uow import UnitOfWork
from tests.models import User, UserRepository, IncompleteRepository


@pytest.mark.asyncio
async def test_delete_user_success(async_session_factory):
    """
    Test successful deletion of a user instance.
    """
    name = "DeleteMe"

    async with UnitOfWork(async_session_factory) as uow:
        user = User(name=name)
        uow.session.add(user)

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == name)
        )
        user = result.scalar_one()
        await UserRepository.delete(uow.session, user)

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == name)
        )
        deleted_user = result.scalar_one_or_none()
        assert deleted_user is None


@pytest.mark.asyncio
async def test_delete_detached_object(async_session_factory):
    """
    Test that deletion of a detached object succeeds (SQLAlchemy queues it).
    """
    name = "DetachedUser"

    async with UnitOfWork(async_session_factory) as uow:
        user = User(name=name)
        uow.session.add(user)

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == name)
        )
        user = result.scalar_one()

    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.delete(uow.session, user)
        await uow.commit()

    async with UnitOfWork(async_session_factory) as uow:
        result = await uow.session.execute(
            sqlalchemy.select(User).where(User.name == name)
        )
        assert result.scalar_one_or_none() is None
