"""
delete_mixin.py

This module provides a reusable async mixin for safely deleting ORM model instances
within a SQLAlchemy-based repository pattern.

Key features:
    - Ensures model class is defined before deletion.
    - Validates that an instance is passed before attempting delete.
    - Designed to be used inside a Unit of Work that manages commit/rollback.
    - Does NOT commit or flush — responsibility is delegated to UoW/session owner.

Typical usage:
    async with UnitOfWork(...) as uow:
        await SomeRepository.delete(uow.session, some_instance)
"""

from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession

from ..base_typing import T
from ..utils import (
    validate_model_defined,
    validate_object_to_update_defined,
    validate_object_instance,
)


class DeleteMixin:
    """
    Mixin for deleting ORM model instances with validation.

    This mixin provides a class method for safely deleting SQLAlchemy model instances
    using an asynchronous session, typically within a Unit of Work (UoW) context.

    Features:
        - Validates that a model is defined on the repository.
        - Ensures a valid object is passed for deletion.
        - Does not commit the session — expects a higher-level UoW to handle it.

    Attributes:
        model (Type[T]): The SQLAlchemy ORM model class to be deleted.
    """

    model = None

    @classmethod
    async def delete(cls: Type[T], asession: AsyncSession, obj: T) -> T:
        """
        Delete an ORM model instance using the provided async session.

        This method performs model and object validation before deletion.
        It does not flush or commit the session — that is the responsibility
        of the calling context (e.g., UnitOfWork).

        :param cls: Repository class inheriting the mixin.
        :param asession: Async SQLAlchemy session.
        :param obj: The ORM model instance to delete.

        :raises RepositoryUsageError: If the model or object is not defined.
        """
        validate_model_defined(cls)
        validate_object_to_update_defined(cls, obj)
        validate_object_instance(cls, obj)
        await asession.delete(obj)
