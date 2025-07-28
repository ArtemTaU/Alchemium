from src.errors.exceptions.base import TemplateError


class QueryExecutionError(TemplateError):
    """Failed to execute query (SQL/type error, etc)."""

    template = "Model '{model}': query execution error '{details}'. {original}"
