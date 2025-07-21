from src.exceptions import TransactionError
from src.exceptions.base import RepositoryError


class RepositoryUsageError(RepositoryError):
    """Incorrect usage of repository (e.g., model not defined, wrong parameters)."""

    template = "Repository usage error: {details}"


class DataValidationError(TransactionError):
    """Invalid data (DataError, wrong type/length/etc)."""

    template = "Invalid data: {details}. {original}"


class QueryExecutionError(RepositoryError):
    """Failed to execute query (SQL/type error, etc)."""

    template = "Model '{model}': query execution error '{details}'. {original}"
