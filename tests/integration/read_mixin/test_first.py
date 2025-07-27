import pytest
from src.uow import UnitOfWork
from tests.models import UserRepository, ProfileRepository, User

from src.exceptions import (
    RelationNotFoundError,
    FieldNotFoundError,
    QueryExecutionError,
    RepositoryUsageError,
    OrderByFieldError,
)


@pytest.mark.asyncio
async def test_first_basic(async_session_factory):
    """
    Test that the first method returns the first user matching the filter.
    """
    users_data = [{"name": "a"}, {"name": "b"}, {"name": "c"}]
    async with UnitOfWork(async_session_factory) as uow:
        for data in users_data:
            await UserRepository.create(uow.session, data)

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.first(asession=uow.session)
        assert user is not None
        assert isinstance(user, User)


@pytest.mark.asyncio
async def test_first_with_filters(async_session_factory):
    """
    Test that filtering by unique field returns the correct user or None.
    """
    user_data = {"name": "unique_first"}
    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.first(
            asession=uow.session, filters={"name": "unique_first"}
        )
        assert user is not None
        assert user.name == "unique_first"

        none_user = await UserRepository.first(
            asession=uow.session, filters={"name": "not_exist"}
        )
        assert none_user is None


@pytest.mark.asyncio
async def test_first_with_order_by(async_session_factory):
    """
    Test that order_by in first returns the expected user.
    """
    users_data = [{"name": "Zed"}, {"name": "Amy"}, {"name": "Bob"}]
    async with UnitOfWork(async_session_factory) as uow:
        for data in users_data:
            await UserRepository.create(uow.session, data)

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.first(asession=uow.session, order_by="name")
        assert user.name == "Amy"


@pytest.mark.asyncio
async def test_first_with_joins(async_session_factory):
    """
    Test that joins work in first method and related data is loaded.
    """
    user_data = {"name": "firstjoin"}
    profile_data = {"bio": "Bio first join"}

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.create(uow.session, user_data)
        await uow.session.flush()
        await ProfileRepository.create(
            uow.session, {**profile_data, "user_id": user.id}
        )

    async with UnitOfWork(async_session_factory) as uow:
        user = await UserRepository.first(
            asession=uow.session,
            filters={"name": "firstjoin"},
            joins=["profile"],
        )
        assert user is not None
        assert user.profile is not None
        assert user.profile.bio == profile_data["bio"]


@pytest.mark.asyncio
async def test_first_field_not_found(async_session_factory):
    """
    Should raise FieldNotFoundError if filter field is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(FieldNotFoundError):
            await UserRepository.first(
                asession=uow.session, filters={"notafield": "xxx"}
            )


@pytest.mark.asyncio
async def test_first_relation_not_found(async_session_factory):
    """
    Should raise RelationNotFoundError if join relation is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(RelationNotFoundError):
            await UserRepository.first(asession=uow.session, joins=["notarelation"])


@pytest.mark.asyncio
async def test_first_order_by_field_not_found(async_session_factory):
    """
    Should raise OrderByFieldError if order_by field is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(OrderByFieldError):
            await UserRepository.first(asession=uow.session, order_by="notafield")


@pytest.mark.asyncio
async def test_first_query_execution_error(async_session_factory):
    """
    Should raise QueryExecutionError if SQLAlchemy throws data/type error.
    """
    user_data = {"name": "FirstTypeError"}
    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(QueryExecutionError):
            await UserRepository.first(
                asession=uow.session,
                filters={"id": {"some": "dict"}},
            )


@pytest.mark.asyncio
async def test_first_repository_usage_error():
    """
    Should raise RepositoryUsageError if model is not defined in repository.
    """

    class NoModelRepo(UserRepository):
        model = None

    class DummySession:
        pass

    with pytest.raises(RepositoryUsageError):
        await NoModelRepo.first(asession=DummySession())
