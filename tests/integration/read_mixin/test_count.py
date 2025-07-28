import pytest
from alchemium import UnitOfWork
from tests.models import UserRepository, ProfileRepository, User

from alchemium.errors import (
    FieldNotFoundError,
    QueryExecutionError,
    RepositoryUsageError,
)


@pytest.mark.asyncio
async def test_count_users_by_name(async_session_factory):
    """
    Should return correct count of users with a given name.
    """
    user_data_1 = {"name": "unique_user1", "position": "Manager"}
    user_data_2 = {"name": "unique_user2", "position": "Manager"}
    user_data_3 = {"name": "unique_user3", "position": "Programmer"}
    users_data = [user_data_1, user_data_2, user_data_3]

    async with UnitOfWork(async_session_factory) as uow:
        for data in users_data:
            await UserRepository.create(uow.session, data)

    async with UnitOfWork(async_session_factory) as uow:
        count = await UserRepository.count(
            asession=uow.session,
            filters={"position": "Manager"},
        )
        assert count == 2


@pytest.mark.asyncio
async def test_count_users_no_matches(async_session_factory):
    """
    Should return zero if no matching users found.
    """
    async with UnitOfWork(async_session_factory) as uow:
        count = await UserRepository.count(
            asession=uow.session,
            filters={"name": "NobodyHere"},
        )
        assert count == 0


@pytest.mark.asyncio
async def test_count_all_users(async_session_factory):
    """
    Should return count of all users if no filter is provided.
    """
    # Create three users
    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, {"name": "Alice"})
        await UserRepository.create(uow.session, {"name": "Bob"})
        await UserRepository.create(uow.session, {"name": "Charlie"})

    async with UnitOfWork(async_session_factory) as uow:
        count = await UserRepository.count(asession=uow.session)
        assert count == 3


@pytest.mark.asyncio
async def test_count_by_foreign_key(async_session_factory):
    """
    Should return correct count for profiles filtered by user_id.
    """
    user_data = {"name": "FKUser"}
    profile_data = {"bio": "FK profile"}

    async with UnitOfWork(async_session_factory) as uow:
        user: User = await UserRepository.create(uow.session, user_data)
        await uow.session.flush()
        await ProfileRepository.create(
            uow.session, {**profile_data, "user_id": user.id}
        )

    async with UnitOfWork(async_session_factory) as uow:
        count = await ProfileRepository.count(
            asession=uow.session,
            filters={"user_id": user.id},
        )
        assert count == 1


@pytest.mark.asyncio
async def test_count_field_not_found(async_session_factory):
    """
    Should raise FieldNotFoundError if filter field does not exist.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(FieldNotFoundError) as exc_info:
            await UserRepository.count(
                asession=uow.session,
                filters={"not_a_field": "test"},
            )
        assert "filter field" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_count_query_execution_error(async_session_factory):
    """
    Should raise QueryExecutionError for invalid data in filter (e.g., type mismatch).
    """
    user_data = {"name": "ErrorUser"}
    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(QueryExecutionError) as excinfo:
            await UserRepository.count(
                asession=uow.session,
                filters={"id": {"bad": "dict"}},
            )
        assert "query execution error" in str(excinfo.value).lower()


@pytest.mark.asyncio
async def test_count_repository_usage_error():
    """
    Should raise RepositoryUsageError if model is not defined in repository.
    """

    class NoModelRepo(UserRepository):
        model = None

    class DummySession:
        pass

    with pytest.raises(RepositoryUsageError) as exc_info:
        await NoModelRepo.count(asession=DummySession(), filters={"name": "test"})
    assert "must define model attribute" in str(exc_info.value).lower()
