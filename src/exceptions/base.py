class RepositoryError(Exception):
    """Base exception for repository/repo+UoW operations."""


# --- Transaction (write) errors ---
class TransactionError(RepositoryError):
    """Base error for any commit/transaction failure."""


class UniqueViolation(TransactionError):
    """Unique constraint violation."""


class ForeignKeyViolation(TransactionError):
    """Foreign key constraint violation."""


class DataValidationError(TransactionError):
    """Invalid data (DataError, wrong type/length/etc)."""


class UnknownTransactionError(TransactionError):
    """Any other unexpected error during transaction."""


# --- Read/query errors ---
class QueryError(RepositoryError):
    """Base error for all query (read) operations."""


class RelationNotFoundError(QueryError):
    """Specified relation for join was not found."""


class FieldNotFoundError(QueryError):
    """Filter references a non-existent model field."""


class QueryExecutionError(QueryError):
    """Failed to execute query (SQL/type error, etc)."""


class OrderByFieldError(QueryError):
    """Specified order_by field does not exist or is invalid."""


class PaginationParameterError(QueryError):
    """Invalid pagination parameters (skip, limit, etc)."""


# --- Usage errors ---
class RepositoryUsageError(RepositoryError):
    """Incorrect usage of repository (e.g., model not defined, wrong parameters)."""
