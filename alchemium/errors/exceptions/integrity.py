from .base import TemplateError


class UniqueViolation(TemplateError):
    """Unique constraint violation."""

    template = "Unique constraint violation. {original}"


class ForeignKeyViolation(TemplateError):
    """Foreign key constraint violation."""

    template = "Foreign key constraint violation. {original}"
