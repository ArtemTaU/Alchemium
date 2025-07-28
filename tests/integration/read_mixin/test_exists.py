import pytest
from src.uow import UnitOfWork
from tests.models import UserRepository, ProfileRepository, User

from src.errors import (
    RelationNotFoundError,
    FieldNotFoundError,
    QueryExecutionError,
    RepositoryUsageError,
)


@pytest.mark.asyncio
async def test_exists_basic(async_session_factory):
    """
    Test that exists returns True if a record exists, False otherwise.
    """
    user_data = {"name": "exists_user"}
    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    async with UnitOfWork(async_session_factory) as uow:
        exists = await UserRepository.exists(
            asession=uow.session, filters={"name": "exists_user"}
        )
        assert exists is True

        not_exists = await UserRepository.exists(
            asession=uow.session, filters={"name": "not_exist_user"}
        )
        assert not_exists is False


@pytest.mark.asyncio
async def test_exists_with_joins(async_session_factory):
    """
    Test that exists works with joins.
    """
    user_data = {"name": "existsjoin"}
    profile_data = {"bio": "ExistsJoinBio"}
    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.create(uow.session, user_data)
        await uow.session.flush()
        await ProfileRepository.create(
            uow.session, {**profile_data, "user_id": user.id}
        )

    async with UnitOfWork(async_session_factory) as uow:
        exists = await UserRepository.exists(
            asession=uow.session, filters={"name": "existsjoin"}, joins=["profile"]
        )
        assert exists is True


@pytest.mark.asyncio
async def test_exists_field_not_found(async_session_factory):
    """
    Should raise FieldNotFoundError if filter field is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(FieldNotFoundError):
            await UserRepository.exists(
                asession=uow.session, filters={"notafield": "xxx"}
            )


@pytest.mark.asyncio
async def test_exists_relation_not_found(async_session_factory):
    """
    Should raise RelationNotFoundError if join relation is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(RelationNotFoundError):
            await UserRepository.exists(asession=uow.session, joins=["notarelation"])


@pytest.mark.asyncio
async def test_exists_query_execution_error(async_session_factory):
    """
    Should raise QueryExecutionError if SQLAlchemy throws data/type error.
    """
    user_data = {"name": "ExistsTypeError"}
    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(QueryExecutionError):
            await UserRepository.exists(
                asession=uow.session,
                filters={"id": {"some": "dict"}},
            )


@pytest.mark.asyncio
async def test_exists_repository_usage_error():
    """
    Should raise RepositoryUsageError if model is not defined in repository.
    """

    class NoModelRepo(UserRepository):
        model = None

    class DummySession:
        pass

    with pytest.raises(RepositoryUsageError):
        await NoModelRepo.exists(asession=DummySession())
