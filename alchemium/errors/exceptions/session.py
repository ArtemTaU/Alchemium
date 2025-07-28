from .base import TemplateError


class SessionActivityError(TemplateError):
    """Error for session activity check."""

    template = "Session is not active"


class SessionFlushError(TemplateError):
    """Error for flush failure."""

    template = "Flush failed. {original}"


class TransactionError(TemplateError):
    """Base error for any commit/transaction failure."""

    template = "Transaction failed. {original}"


class UnknownTransactionError(TemplateError):
    """Any other unexpected error during transaction."""

    template = "Unexpected error during transaction. {details}. {original}"
