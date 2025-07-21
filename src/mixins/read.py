from typing import Type, Optional, Dict, Any, Sequence

from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError, StatementError, DataError, ArgumentError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..typing import T

from ..exceptions import (
    QueryError,
    RelationNotFoundError,
    FieldNotFoundError,
    QueryExecutionError,
    OrderByFieldError,
    PaginationParameterError,
    RepositoryUsageError,
)


class ReadMixin:
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

        if joins:
            for rel in joins:
                try:
                    join_attr = getattr(cls.model, rel)
                    stmt = stmt.options(selectinload(join_attr))
                except (AttributeError, InvalidRequestError, ArgumentError) as exc:
                    raise RelationNotFoundError(
                        model=model_name,
                        rel=rel,
                        original=f" Original error: {exc}" if exc else "",
                    ) from exc

        if filters:
            for k, v in filters.items():
                try:
                    attr = getattr(cls.model, k, None)
                    if attr is None:
                        raise FieldNotFoundError(
                            model=model_name,
                            field=k,
                            original="",
                        )
                    stmt = stmt.where(attr == v)
                except FieldNotFoundError:
                    raise
                except AttributeError as exc:
                    raise FieldNotFoundError(
                        model=model_name,
                        field=k,
                        original="",
                    ) from exc
                except Exception as exc:
                    raise QueryError(
                        model=model_name,
                        field=k,
                        original=f" Original error: {exc}" if exc else "",
                    ) from exc

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
