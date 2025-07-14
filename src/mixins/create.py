from typing import Type, Dict, Any
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.ext.asyncio import AsyncSession

from ..typing import T
from ..interfaces import ICreateRepository

from ..exceptions import (
    UniqueViolation,
    ForeignKeyViolation,
    DataValidationError,
    TransactionError,
    CreateError,
    UnknownCreateError,
)


class CreateMixin:
    model = None

    @classmethod
    async def create(cls: Type[T], asession: AsyncSession, data: Dict[str, Any]) -> T:
        """
        Create a new record in the database.

        :param asession: Async database session.
        :param data: Data to create a new record (dict).
        :return: Created model instance.
        :raises IntegrityError: If a constraint (like unique) is violated.
        :raises SQLAlchemyError: For any other SQLAlchemy-related error.
        """
        if cls.model is None:
            raise NotImplementedError("Repository must define model attribute")
        obj = cls.model(**data)
        asession.add(obj)
        try:
            await asession.commit()
            await asession.refresh(obj)
        except IntegrityError as exc:
            await asession.rollback()
            if "unique" in str(exc.orig).lower():
                raise UniqueViolation from exc
            if "foreign key" in str(exc.orig).lower():
                raise ForeignKeyViolation from exc
            raise CreateError from exc
        except DataError as exc:
            await asession.rollback()
            raise DataValidationError from exc
        except SQLAlchemyError as exc:
            await asession.rollback()
            raise TransactionError from exc
        except Exception as exc:
            await asession.rollback()
            raise UnknownCreateError from exc
        return obj
