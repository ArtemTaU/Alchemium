from typing import Type, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..exceptions import (
    RepositoryUsageError,
    DataValidationError,
    UnknownTransactionError,
)
from ..queries import ModelInitializer, SessionAdder

from ..typing import T
from ..utils import validate_model_defined


class CreateMixin(ModelInitializer, SessionAdder):
    """
    Mixin for creating new ORM records with standardized error handling.

    Provides a classmethod to safely instantiate and add new SQLAlchemy model
    instances to an async session, raising consistent and informative exceptions
    on errors. The operation does NOT commit the session.

    Attributes:
        model (Type[T]): The SQLAlchemy ORM model class to create.
    """

    model = None

    @classmethod
    async def create(cls: Type[T], asession: AsyncSession, data: Dict[str, Any]) -> T:
        """
        Create a new ORM model instance and add it to the async session with error handling.

        :param asession: The asynchronous SQLAlchemy session.
        :param data: Dict of attributes for the model.
        :return: The newly created ORM model instance.
        :raises RepositoryUsageError: If the repository does not define model attribute.
        :raises DataValidationError: If the provided data is invalid for model construction.
        :raises UnknownTransactionError: For any other unexpected error during object creation.
        """
        validate_model_defined(cls)

        model_name = getattr(cls.model, "__name__", str(cls.model))
        obj = cls.initialize(data, model_name)
        cls.session_add(asession, obj, model_name)

        return obj
