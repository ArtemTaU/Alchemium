from .base import TemplateError


class TransactionError(TemplateError):
    """Base error for any commit/transaction failure."""

    template = "Transaction failed. {original}"


class UnknownTransactionError(TemplateError):
    """Any other unexpected error during transaction."""

    template = "Unexpected error during transaction. {details}. {original}"
