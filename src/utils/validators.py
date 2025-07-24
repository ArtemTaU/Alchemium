from src.exceptions import RepositoryUsageError


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
