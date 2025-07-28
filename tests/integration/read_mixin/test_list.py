from typing import List

import pytest
from src.uow import UnitOfWork
from tests.models import UserRepository, ProfileRepository, User

from src.errors import (
    RelationNotFoundError,
    FieldNotFoundError,
    QueryExecutionError,
    RepositoryUsageError,
    OrderByFieldError,
    PaginationParameterError,
)


@pytest.mark.asyncio
async def test_list_users_basic(async_session_factory):
    """
    Test that the list method returns all users matching the filter.
    """
    users_data = [{"name": f"user{i}"} for i in range(3)]
    async with UnitOfWork(async_session_factory) as uow:
        for data in users_data:
            await UserRepository.create(uow.session, data)

    async with UnitOfWork(async_session_factory) as uow:
        users: List[User] = await UserRepository.list(
            asession=uow.session,
            filters=None,
        )
        assert isinstance(users, list)
        names = [u.name for u in users]
        for data in users_data:
            assert data["name"] in names


@pytest.mark.asyncio
async def test_list_with_filters_unique_name(async_session_factory):
    """
    Test that filtering by unique field (name) in list method returns at most one user.
    """
    user_data_1 = {"name": "unique_user1"}
    user_data_2 = {"name": "unique_user2"}
    user_data_3 = {"name": "unique_user3"}
    users_data = [user_data_1, user_data_2, user_data_3]

    async with UnitOfWork(async_session_factory) as uow:
        for data in users_data:
            await UserRepository.create(uow.session, data)

    async with UnitOfWork(async_session_factory) as uow:
        for user_data in users_data:
            users: List[User] = await UserRepository.list(
                asession=uow.session,
                filters={"name": user_data["name"]},
            )
            assert len(users) == 1
            assert users[0].name == user_data["name"]

    async with UnitOfWork(async_session_factory) as uow:
        users: List[User] = await UserRepository.list(
            asession=uow.session,
            filters={"name": "nonexistent_user"},
        )
        assert len(users) == 0


@pytest.mark.asyncio
async def test_list_with_order_by(async_session_factory):
    """
    Test that order_by works in list method.
    """
    users_data = [{"name": "Zed"}, {"name": "Amy"}, {"name": "Bob"}]
    async with UnitOfWork(async_session_factory) as uow:
        for data in users_data:
            await UserRepository.create(uow.session, data)

    async with UnitOfWork(async_session_factory) as uow:
        users: List[User] = await UserRepository.list(
            asession=uow.session,
            order_by="name",
        )
        names = [u.name for u in users]
        assert names == sorted(names)


@pytest.mark.asyncio
async def test_list_with_pagination(async_session_factory):
    """
    Test that skip (offset) and limit (pagination) work in list method.
    """
    users_data = [{"name": f"user{i}"} for i in range(10)]
    async with UnitOfWork(async_session_factory) as uow:
        for data in users_data:
            await UserRepository.create(uow.session, data)

    async with UnitOfWork(async_session_factory) as uow:
        users: List[User] = await UserRepository.list(
            asession=uow.session, skip=5, limit=3, order_by="name"
        )
        assert len(users) == 3
        expected_names = sorted([u["name"] for u in users_data])[5:8]
        assert [u.name for u in users] == expected_names


@pytest.mark.asyncio
async def test_list_with_joins(async_session_factory):
    """
    Test that joins work in list method and related data is loaded.
    """
    user_data = {"name": "joinlist"}
    profile_data = {"bio": "Bio join"}

    async with UnitOfWork(async_session_factory) as uow:
        user: User = await UserRepository.create(uow.session, user_data)
        await uow.session.flush()
        await ProfileRepository.create(
            uow.session, {**profile_data, "user_id": user.id}
        )

    async with UnitOfWork(async_session_factory) as uow:
        users: List[User] = await UserRepository.list(
            asession=uow.session,
            filters={"name": "joinlist"},
            joins=["profile"],
        )
        assert len(users) == 1
        user = users[0]
        assert user.profile is not None
        assert user.profile.bio == profile_data["bio"]


@pytest.mark.asyncio
async def test_list_field_not_found(async_session_factory):
    """
    Should raise FieldNotFoundError if filter field is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(FieldNotFoundError):
            await UserRepository.list(
                asession=uow.session,
                filters={"notafield": "xxx"},
            )


@pytest.mark.asyncio
async def test_list_relation_not_found(async_session_factory):
    """
    Should raise RelationNotFoundError if join relation is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(RelationNotFoundError):
            await UserRepository.list(
                asession=uow.session,
                joins=["notarelation"],
            )


@pytest.mark.asyncio
async def test_list_order_by_field_not_found(async_session_factory):
    """
    Should raise OrderByFieldError if order_by field is invalid.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(OrderByFieldError):
            await UserRepository.list(
                asession=uow.session,
                order_by="notafield",
            )


@pytest.mark.asyncio
async def test_list_pagination_param_error(async_session_factory):
    """
    Should raise PaginationParameterError if skip or limit cause an error.
    """
    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(PaginationParameterError):
            await UserRepository.list(
                asession=uow.session,
                skip="not_an_int",
            )
        with pytest.raises(PaginationParameterError):
            await UserRepository.list(
                asession=uow.session,
                limit="not_an_int",
            )


@pytest.mark.asyncio
async def test_list_query_execution_error(async_session_factory):
    """
    Should raise QueryExecutionError if underlying SQLAlchemy throws data/type error.
    For example: filter by dict on integer field.
    """
    user_data = {"name": "TypeListTest"}
    async with UnitOfWork(async_session_factory) as uow:
        await UserRepository.create(uow.session, user_data)

    async with UnitOfWork(async_session_factory) as uow:
        with pytest.raises(QueryExecutionError):
            await UserRepository.list(
                asession=uow.session,
                filters={"id": {"some": "dict"}},
            )


@pytest.mark.asyncio
async def test_list_repository_usage_error():
    """
    Should raise RepositoryUsageError if model is not defined in repository.
    """

    class NoModelRepo(UserRepository):
        model = None

    class DummySession:
        pass

    with pytest.raises(RepositoryUsageError):
        await NoModelRepo.list(asession=DummySession())
