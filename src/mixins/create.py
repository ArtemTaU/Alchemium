from typing import Type, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..exceptions import (
    RepositoryUsageError,
    DataValidationError,
    UnknownTransactionError,
)

from ..typing import T


class CreateMixin:
    model = None

    @classmethod
    async def create(cls: Type[T], asession: AsyncSession, data: Dict[str, Any]) -> T:
        """
        Create a new record in the database. Does NOT commit!
        Args:
            asession (AsyncSession): Async database session.
            data (dict): Data to create a new record.
        Returns:
            T: The newly created ORM model instance.
        Raises:
            RepositoryUsageError: If the repository does not define model attribute.
            DataValidationError: If the provided data is invalid.
            UnknownTransactionError: For any other unexpected error during object creation.
        """
        if cls.model is None:
            raise RepositoryUsageError(
                details=f"{cls.__name__} repository must define model attribute"
            )

        try:
            obj = cls.model(**data)
            asession.add(obj)
            return obj
        except TypeError as exc:
            raise DataValidationError(
                details=f"Invalid argument(s) for model '{getattr(cls.model, '__name__', str(cls.model))}'",
                original=str(exc),
            ) from exc
        except ValueError as exc:
            raise DataValidationError(
                details=f"Invalid value(s) for model '{getattr(cls.model, '__name__', str(cls.model))}'",
                original=str(exc),
            ) from exc
        except Exception as exc:
            raise UnknownTransactionError(
                details=f"Unexpected error while creating '{getattr(cls.model, '__name__', str(cls.model))}'",
                original=str(exc),
            ) from exc
