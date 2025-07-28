from typing import Type, Dict, Any
from ..errors import DataValidationError

from ..typing import T
from ..utils import (
    validate_model_defined,
    validate_object_to_update_defined,
    validate_object_instance,
)


class UpdateMixin:
    """
    Mixin for updating ORM model instances with standardized error handling.

    This mixin provides a classmethod to safely update attributes of an existing SQLAlchemy
    model instance, performing validation before assignment.

    Notes:
        - The method modifies the object in place.
        - It does NOT return the object or persist changes to the database.
        - It should be used in conjunction with a Unit of Work or manual session commit
          to persist updates.

    Attributes:
        model (Type[T]): The SQLAlchemy ORM model class to update.
    """

    model = None

    @classmethod
    def update(cls: Type[T], obj: T, data: Dict[str, Any]) -> T:
        """
        Update an existing ORM model instance with provided data.

        The method only sets attributes that already exist on the model.
        It does not return the updated object or commit to the database.

        :param obj: The ORM model instance to update.
        :param data: Dict of attributes and their new values.

        :raises RepositoryUsageError: If the model attribute is not defined.
        :raises DataValidationError: If any provided key is not a valid attribute.
        """
        validate_model_defined(cls)
        validate_object_to_update_defined(cls, obj)
        validate_object_instance(cls, obj)

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
            else:
                raise DataValidationError(
                    details=f"Invalid argument '{key}' for model '{type(obj).__name__}'"
                )


# Комментарий: есть способ bulk update через алхимию,
# но он не даст такой гибкости. это просто обёртка над setattr
