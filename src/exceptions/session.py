from src.exceptions import TransactionError


class UniqueViolation(TransactionError):
    """Unique constraint violation."""

    template = "Unique constraint violation. {original}"


class ForeignKeyViolation(TransactionError):
    """Foreign key constraint violation."""

    template = "Foreign key constraint violation. {original}"
