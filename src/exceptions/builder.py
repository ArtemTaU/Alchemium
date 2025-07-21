from src.exceptions.base import RepositoryError


class RelationNotFoundError(RepositoryError):
    """Specified relation for join was not found."""

    template = (
        "Model '{model}': relation '{rel}' for join not found or invalid. {original}"
    )


class FieldNotFoundError(RepositoryError):
    """Failed to find field in model."""

    template = "Model '{model}': filter field '{field}' not found. {original}"


class QueryError(RepositoryError):
    """Base error for all query (read) operations."""

    template = "Model '{model}': unknown filter error for field '{field}'. {original}"


class OrderByFieldError(QueryError):
    """Specified order_by field does not exist or is invalid."""

    template = "Model '{model}': specified order_by field '{field}' does not exist or is invalid. {original}"


class PaginationParameterError(QueryError):
    """Invalid pagination parameters (skip, limit, etc)."""

    template = (
        "Model '{model}': invalid pagination parameter '{field}'. {details}. {original}"
    )
