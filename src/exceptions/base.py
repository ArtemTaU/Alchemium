# class RepositoryError(Exception):
#     """Base exception for repository/repo+UoW operations."""


class RepositoryError(Exception):
    """Base error for repository logic."""

    default_template: str = "Repository error occurred."

    def __init__(self, **kwargs):
        template = getattr(self, "template", self.default_template)
        self.message = template.format(
            **{k: kwargs.get(k, "") for k in self._get_template_fields(template)}
        )
        super().__init__(self.message)
        self.kwargs = kwargs

    def __str__(self):
        return self.message

    @staticmethod
    def _get_template_fields(template):
        import string

        return [fname for _, fname, _, _ in string.Formatter().parse(template) if fname]


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

    template = "Model '{model}': unknown filter error for field '{field}'. {original}"


class RelationNotFoundError(RepositoryError):
    """Specified relation for join was not found."""

    template = (
        "Model '{model}': relation '{rel}' for join not found or invalid. {original}"
    )


class FieldNotFoundError(RepositoryError):
    """Failed to find field in model."""

    template = "Model '{model}': filter field '{field}' not found. {original}"


class QueryExecutionError(RepositoryError):
    """Failed to execute query (SQL/type error, etc)."""

    template = "Model '{model}': query execution error '{details}'. {original}"


class OrderByFieldError(QueryError):
    """Specified order_by field does not exist or is invalid."""


class PaginationParameterError(QueryError):
    """Invalid pagination parameters (skip, limit, etc)."""


# --- Usage errors ---
class RepositoryUsageError(RepositoryError):
    """Incorrect usage of repository (e.g., model not defined, wrong parameters)."""

    template = "Repository usage error: {details}"
