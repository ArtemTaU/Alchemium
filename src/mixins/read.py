from typing import Type, Optional, Dict, Any, Sequence, List

from sqlalchemy import select
from sqlalchemy.exc import StatementError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from ..query.builder import QueryBuilder
from ..typing import T

from ..exceptions import (
    QueryExecutionError,
    RepositoryUsageError,
)


class ReadMixin(QueryBuilder):
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
        Получить один объект по фильтрам, c optional join.
        """
        if cls.model is None:
            raise RepositoryUsageError(
                details=f"{cls.__name__} repository must define model attribute"
            )

        model_name = getattr(cls.model, "__name__", str(cls.model))

        stmt = select(cls.model)
        stmt = cls.apply_joins(stmt, joins, model_name)
        stmt = cls.apply_filters(stmt, filters, model_name)

        try:
            result = await asession.execute(stmt)
            return result.scalars().first()
        except (StatementError, DataError) as exc:
            raise QueryExecutionError(
                model=model_name,
                details=str("(data/type issue)"),
                original=f"{exc}",
            ) from exc
        except Exception as exc:
            raise QueryExecutionError(
                model=model_name,
                details=str("(unknown error)"),
                original=f"{exc}",
            ) from exc

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

        try:
            result = await asession.execute(stmt)
            return result.scalars().all()
        except (StatementError, DataError) as exc:
            raise QueryExecutionError(
                model=model_name,
                details=str("(data/type issue)"),
                original=f"{exc}",
            ) from exc
        except Exception as exc:
            raise QueryExecutionError(
                model=model_name,
                details=str("(unknown error)"),
                original=f"{exc}",
            ) from exc
