from src.exceptions import RepositoryUsageError

from ..typing import T


def validate_model_defined(cls):
    """
    Ensure that the model attribute is defined on the class.

    :param cls: The class (repository or mixin) being validated.
    :raises RepositoryUsageError: If the model attribute is None.
    """
    if getattr(cls, "model", None) is None:
        raise RepositoryUsageError(
            details=f"{cls.__name__} repository must define model attribute"
        )


def validate_object_to_update_defined(cls, obj: T):
    """
    Ensure that the model attribute is defined on the class.

    :param cls: The class (repository or mixin) being validated.
    :param obj: ORM model instance to update.
    :raises RepositoryUsageError: If the model attribute is None.
    """
    if obj is None:
        raise RepositoryUsageError(
            details=f"{cls.__name__} Object to update must be provided"
        )
