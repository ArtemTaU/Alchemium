from typing import Type, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..exceptions import DataValidationError

from ..typing import T
from ..utils import validate_model_defined, validate_object_to_update_defined


class UpdateMixin:
    """
    Mixin for updating ORM model instances with standardized error handling.

    Provides a classmethod to update an existing SQLAlchemy model instance with new data,
    handling validation and session commit/refresh. Raises informative exceptions on error.

    Attributes:
        model (Type[T]): The SQLAlchemy ORM model class to update.
    """

    model = None

    @classmethod
    async def update(
        cls: Type[T], asession: AsyncSession, obj: T, data: Dict[str, Any]
    ) -> T:
        """
        Update an existing ORM model instance and commit changes with error handling.

        :param asession: The asynchronous SQLAlchemy session.
        :param obj: The ORM model instance to update.
        :param data: Dict of attributes and their new values.
        :return: The updated ORM model instance.
        :raises RepositoryUsageError: If the model attribute is not defined.
        :raises DataValidationError: If the provided data is invalid for model.
        :raises UnknownTransactionError: For any other unexpected error during update.
        """
        validate_model_defined(cls)
        validate_object_to_update_defined(cls, obj)

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
            else:
                raise DataValidationError(
                    details=f"'{key}' for model '{type(obj).__name__}'"
                )

        return obj


# Комментарий: есть способbulk update через алхимию, но он не даст такой гибкости.
