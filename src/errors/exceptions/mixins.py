from .base import TemplateError


class RepositoryUsageError(TemplateError):
    """Incorrect usage of repository (e.g., model not defined, wrong parameters)."""

    template = "Repository usage error: {details}"


class DataValidationError(TemplateError):
    """Invalid data (DataError, wrong type/length/etc)."""

    template = "Invalid data: {details}. {original}"
