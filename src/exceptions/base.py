class RepositoryError(Exception):
    """Base exception for repository/repo+UoW operations."""


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
