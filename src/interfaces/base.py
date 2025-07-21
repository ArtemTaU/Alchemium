from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

from ..typing import T


class ICreateRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, asession: AsyncSession, data: Dict[str, Any]) -> T:
        """
        Create a new record in the database.

        :param asession: Async database session.
        :param data: Data to create a new record.
        :return: Created model instance.
        """
        raise NotImplementedError("Create method not implemented")


class IReadRepository(ABC, Generic[T]):
    @abstractmethod
    async def get(
        self,
        asession: AsyncSession,
        *,
        filters: dict = None,
        joins: list[str] = None,
    ) -> Optional[T]:
        """
        Retrieve a single record matching filters.

        :param asession: Async database session.
        :param filters: Dict with filters to apply.
        :param joins: List of related models to join/prefetch.
        :return: Model instance or None.
        """
        raise NotImplementedError("Get method not implemented")

    @abstractmethod
    async def list(
        self,
        asession: AsyncSession,
        *,
        filters: dict = None,
        order_by: Optional[str] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        joins: List[str] = None,
    ) -> list[T]:
        """
        Retrieve a list of records matching filters, with optional ordering and pagination.

        :param asession: Async database session.
        :param filters: Dict with filters to apply.
        :param order_by: Field name to order results.
        :param skip: Number of records to skip.
        :param limit: Max number of records to return.
        :param joins: List of related models to join/prefetch.
        :return: List of model instances.
        """
        raise NotImplementedError("List method not implemented")

    @abstractmethod
    async def count(
        self,
        asession: AsyncSession,
        filters: dict = None,
    ) -> int:
        """
        Count records matching filters.

        :param asession: Async database session.
        :param filters: Dict with filters to apply.
        :return: Number of matching records.
        """
        raise NotImplementedError("Count method not implemented")

    @abstractmethod
    async def first(
        self,
        asession: AsyncSession,
        *,
        filters: dict = None,
        order_by: Optional[str] = None,
        joins: List[str] = None,
    ) -> Optional[T]:
        """
        Retrieve the first record matching filters (with optional ordering).

        :param asession: Async database session.
        :param filters: Dict with filters to apply.
        :param order_by: Field name to order results.
        :param joins: List of related models to join/prefetch.
        :return: Model instance or None.
        """
        raise NotImplementedError("First method not implemented")

    @abstractmethod
    async def exists(
        self,
        asession: AsyncSession,
        *,
        filters: Optional[dict] = None,
    ) -> bool:
        """
        Check if any record exists matching filters.

        :param asession: Async database session.
        :param filters: Dict with filters to apply.
        :return: True if exists, False otherwise.
        """
        raise NotImplementedError("Exists method not implemented")


class IUpdateRepository(ABC, Generic[T]):
    @abstractmethod
    async def update(
        self,
        asession: AsyncSession,
        instance: T,
        data: Dict[str, Any],
    ) -> T:
        """
        Update an existing record.

        :param asession: Async database session.
        :param instance: Model instance to update.
        :param data: Data to update the instance.
        :return: Updated model instance.
        """
        raise NotImplementedError("Update method not implemented")


class IDeleteRepository(ABC, Generic[T]):
    @abstractmethod
    async def delete(self, asession: AsyncSession, instance: T) -> None:
        """
        Delete a record from the database.

        :param asession: Async database session.
        :param instance: Model instance to delete.
        """
        raise NotImplementedError("Delete method not implemented")
