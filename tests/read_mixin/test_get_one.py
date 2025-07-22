import pytest
from src.uow import UnitOfWork
from tests.models import UserRepository, ProfileRepository

from src.exceptions import (
    RelationNotFoundError,
    FieldNotFoundError,
    QueryExecutionError,
    RepositoryUsageError,
)


@pytest.mark.asyncio
async def test_get_one_user(async_session_factory):
    """
    Test that an existing user can be read from the database via repository's get_one method.

    Steps:
        1. Create and commit a user in the database.
        2. Use repository's get_one to retrieve user by filter (name).
        3. Assert that retrieved user matches expected data.

    Args:
        async_session_factory (async_sessionmaker): Fixture providing session factory for UoW.
    """
    # Step 1: Create user
    user_data = {"name": "Readium"}

    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    # Step 2: Read user using repository
    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.get_one(
            asession=uow.session,
            filters={"name": "Readium"},
        )
        # Step 3: Assert
        assert user is not None
        assert user.name == "Readium"


@pytest.mark.asyncio
async def test_get_one_user_with_profile(async_session_factory):
    """
    Tests that get_one with a join returns a user with a profile.

    This test creates a user and an associated profile in the database,
    then reads the user back using the repository's get_one method with a join
    to the profile. It verifies that the profile is loaded and its data is correct.

    Args:
        async_session_factory (async_sessionmaker):
            Fixture providing a session factory for the UnitOfWork.

    Asserts:
        - The user is found (not None).
        - The user's name matches the expected value.
        - The user has a profile attached (not None).
        - The profile's bio matches the expected value.
    """
    user_data = {"name": "JoinedUser"}
    profile_data = {"bio": "Tester bio"}

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.create(uow.session, user_data)
        await uow.session.flush()
        await ProfileRepository.create(
            uow.session, {**profile_data, "user_id": user.id}
        )

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.get_one(
            asession=uow.session, filters={"name": "JoinedUser"}, joins=["profile"]
        )
        assert user is not None
        assert user.name == user_data.get("name")
        assert user.profile is not None
        assert user.profile.bio == profile_data.get("bio")


@pytest.mark.asyncio
async def test_get_one_profile_by_user_id(async_session_factory):
    """
    Tests that filtering by foreign key works for ProfileRepository.

    This test creates a user and a profile linked to that user.
    It then reads the profile back using the repository's get_one method,
    filtering by user_id and joining the user.
    It verifies that the joined user and profile have the correct data.

    Args:
        async_session_factory (async_sessionmaker):
            Fixture providing a session factory for the UnitOfWork.

    Asserts:
        - The profile is found (not None).
        - The profile's bio matches the expected value.
        - The joined user exists and has the expected name.
    """
    user_data = {"name": "HasProfile"}
    profile_data = {"bio": "Bio for profile"}

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.create(uow.session, user_data)
        await uow.session.flush()
        await ProfileRepository.create(
            uow.session, {**profile_data, "user_id": user.id}
        )

    async with UnitOfWork(async_session_factory) as uow:
        result = await ProfileRepository.get_one(
            asession=uow.session,
            filters={"user_id": user.id},
            joins=["user"],
        )
        assert result is not None
        assert result.bio == profile_data.get("bio")
        assert result.user.name == user_data.get("name")


@pytest.mark.asyncio
async def test_get_one_field_not_found(async_session_factory):
    """
    Should raise FieldNotFoundError if filter field is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(FieldNotFoundError) as excinfo:
            await UserRepository.get_one(
                asession=uow.session,
                filters={"nonexistent_field": "value"},
            )
        assert (
            "filter field 'nonexistent_field' not found" in str(excinfo.value).lower()
        )


@pytest.mark.asyncio
async def test_get_one_relation_not_found(async_session_factory):
    """
    Should raise RelationNotFoundError if join relation is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(RelationNotFoundError) as excinfo:
            await UserRepository.get_one(
                asession=uow.session,
                joins=["nonexistent_relation"],
            )
        assert (
            "relation 'nonexistent_relation' for join not found"
            in str(excinfo.value).lower()
        )


@pytest.mark.asyncio
async def test_get_one_query_execution_error(async_session_factory):
    """
    Should raise QueryExecutionError if underlying SQLAlchemy throws data/type error.
    For example: filter by dict on integer field.
    """
    user_data = {"name": "DataTypeTest"}
    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(QueryExecutionError) as excinfo:
            await UserRepository.get_one(
                asession=uow.session,
                filters={"id": {"some": "dict"}},
            )
        assert "query execution error" in str(excinfo.value).lower()


@pytest.mark.asyncio
async def test_repository_usage_error():
    """
    Should raise RepositoryUsageError if model is not defined in repository.
    """

    class NoModelRepo(UserRepository):
        model = None

    class DummySession:
        pass

    with pytest.raises(RepositoryUsageError) as excinfo:
        await NoModelRepo.get_one(asession=DummySession(), filters={"name": "test"})
    assert "must define model attribute" in str(excinfo.value).lower()
