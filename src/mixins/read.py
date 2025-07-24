from typing import Type, Optional, Dict, Any, Sequence, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..queries import *
from ..typing import T

from ..exceptions import (
    RepositoryUsageError,
)


class ReadMixin(QueryBuilder, QueryExecutor):
    model = None

    @classmethod
    async def get_one(
        cls: Type[T],
        *,
        asession: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        joins: Optional[Sequence[str]] = None,
    ) -> Optional[T]:
        """
        Retrieve a single object matching the specified filters, with optional joins.

        :param asession: Async database session.
        :param filters: Optional dictionary of filter conditions to apply.
        :param joins: Optional list/sequence of related models to join.
        :return: Instance of the model if found, otherwise None.
        :raises RelationNotFoundError: If join attribute not found or invalid.
        :raises FieldNotFoundError: If field is not found in model.
        :raises QueryError: For other unknown filter errors.
        :raises RepositoryUsageError: If the model attribute is not defined in the repository.
        :raises QueryExecutionError: If there are issues executing the query.
        """
        if cls.model is None:
            raise RepositoryUsageError(
                details=f"{cls.__name__} repository must define model attribute"
            )

        model_name = getattr(cls.model, "__name__", str(cls.model))

        stmt = select(cls.model)
        stmt = cls.apply_joins(stmt, joins, model_name)
        stmt = cls.apply_filters(stmt, filters, model_name)

        result = await cls.execute(stmt, asession, model_name)
        return result.scalars().first()

    @classmethod
    async def list(
        cls: Type[T],
        *,
        asession: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        joins: Optional[List[str]] = None,
    ) -> List[T]:
        """
        Retrieve a list of records matching filters, with optional ordering and pagination.

        :param asession: Async database session.
        :param filters: Dict with filters to apply.
        :param order_by: Field name to order results.
        :param skip: Number of records to skip.
        :param limit: Max number of records to return.
        :param joins: List of related models to join/prefetch.
        :return: List of model instances.
        :raises RelationNotFoundError: If join attribute not found or invalid.
        :raises FieldNotFoundError: If field is not found in model.
        :raises QueryError: For other unknown filter errors.
        :raises OrderByFieldError: If order_by field is invalid.
        :raises PaginationParameterError: If skip or limit cause an error.
        :raises RepositoryUsageError: If the model attribute is not defined in the repository.
        :raises QueryExecutionError: If there are issues executing the query.
        """
        if cls.model is None:
            raise RepositoryUsageError(
                details=f"{cls.__name__} repository must define model attribute"
            )

        model_name = getattr(cls.model, "__name__", str(cls.model))

        stmt = select(cls.model)
        stmt = cls.apply_joins(stmt, joins, model_name)
        stmt = cls.apply_filters(stmt, filters, model_name)
        stmt = cls.apply_order_by(stmt, order_by, model_name)
        stmt = cls.apply_pagination(stmt, skip, limit, model_name)

        result = await cls.execute(stmt, asession, model_name)
        return result.scalars().all()

    @classmethod
    async def count(
        cls,
        *,
        asession: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Count records matching filters.

        :param asession: Async database session.
        :param filters: Dict with filters to apply.
        :return: Number of matching records.
        :raises RepositoryUsageError: If the model attribute is not defined in the repository.
        """
        if cls.model is None:
            raise RepositoryUsageError(
                details=f"{cls.__name__} repository must define model attribute"
            )

        model_name = getattr(cls.model, "__name__", str(cls.model))

        stmt = select(func.count()).select_from(cls.model)
        stmt = cls.apply_filters(stmt, filters, model_name)

        result = await cls.execute(stmt, asession, model_name)
        return result.scalar_one()

    @classmethod
    async def first(
        cls,
        *,
        asession: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        joins: Optional[List[str]] = None,
    ) -> Optional[T]:
        """
        Retrieve the first record matching filters (with optional ordering and joins).

        :param asession: Async database session.
        :param filters: Optional dictionary of filter conditions to apply.
        :param order_by: Field name to order results.
        :param joins: Optional list of related models to join/prefetch.
        :return: The first model instance if found, otherwise None.
        :raises RepositoryUsageError: If the model attribute is not defined in the repository.
        :raises RelationNotFoundError: If join attribute not found or invalid.
        :raises FieldNotFoundError: If filter field is not found in model.
        :raises QueryError: For other unknown filter errors.
        :raises OrderByFieldError: If order_by field is invalid.
        :raises QueryExecutionError: If there are issues executing the query.
        """
        records = await cls.list(
            asession=asession,
            filters=filters,
            order_by=order_by,
            skip=None,
            limit=1,
            joins=joins,
        )
        return records[0] if records else None

    @classmethod
    async def exists(
        cls,
        *,
        asession: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        joins: Optional[List[str]] = None,
    ) -> bool:
        """
        Check if any record exists matching filters.

        :param asession: Async database session.
        :param filters: Optional dictionary of filter conditions to apply.
        :param joins: Optional list of related models to join/prefetch.
        :return: True if at least one record exists, False otherwise.
        :raises RepositoryUsageError: If the model attribute is not defined in the repository.
        :raises RelationNotFoundError: If join attribute not found or invalid.
        :raises FieldNotFoundError: If filter field is not found in model.
        :raises QueryError: For other unknown filter errors.
        :raises QueryExecutionError: If there are issues executing the query.
        """
        records = await cls.list(
            asession=asession,
            filters=filters,
            limit=1,
            joins=joins,
        )
        return bool(records)
