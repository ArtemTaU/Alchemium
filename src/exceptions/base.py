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


# --- Transaction errors ---
class TransactionError(RepositoryError):
    """Base error for any commit/transaction failure."""

    template = "Transaction failed. {original}"


class UnknownTransactionError(TransactionError):
    """Any other unexpected error during transaction."""

    template = "Unexpected error during transaction. {details}. {original}"
