from typing import Any

from sqlalchemy.exc import StatementError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions import (
    QueryExecutionError,
    UnknownTransactionError,
    DataValidationError,
)
from src.typing import ModelType, T


class SessionAdder:
    """
    Utility class for adding model instances to a SQLAlchemy session with error handling.

    This class provides a classmethod to add an ORM object to an async session,
    catching and re-raising errors with detailed exception information.
    """

    @classmethod
    def session_add(
        cls,
        asession: AsyncSession,
        obj: object,
        model_name: str,
    ) -> None:
        """
        Add an ORM object to the async SQLAlchemy session with error handling.

        :param asession: The asynchronous SQLAlchemy session.
        :param obj: The ORM model instance to add.
        :param model_name: Name of the model (for error reporting).
        :raises UnknownTransactionError: If any error occurs during add.
        """
        try:
            asession.add(obj)
        except Exception as exc:
            raise UnknownTransactionError(
                details=f"Unexpected error while adding '{model_name}' to session",
                original=str(exc),
            ) from exc


class QueryExecutor:
    """
    Utility class for executing SQLAlchemy queries with standardized error handling.

    This class provides a static method to execute a SQLAlchemy statement using
    an asynchronous session, catching and re-raising database exceptions as a
    custom `QueryExecutionError` with helpful details.
    """

    @staticmethod
    async def execute(
        stmt,
        asession: AsyncSession,
        model_name: str,
    ) -> Any:
        """
        Executes a SQLAlchemy statement using the provided asynchronous session,
        with error handling.

        :param stmt: The SQLAlchemy statement to execute.
        :param asession: The asynchronous SQLAlchemy session.
        :param model_name: Name of the model being queried (used for error reporting).
        :return: The result of the executed statement.
        :raises QueryExecutionError: If a database error occurs during execution.
        """
        try:
            return await asession.execute(stmt)
        except (StatementError, DataError) as exc:
            raise QueryExecutionError(
                model=model_name,
                details=str("(data/type issue)"),
                original=f"{exc}",
            ) from exc
        except Exception as exc:
            raise QueryExecutionError(
                model=model_name,
                details=str("(unknown error)"),
                original=f"{exc}",
            ) from exc


class ModelInitializer:
    """
    Utility class for instantiating SQLAlchemy models with standardized error handling.

    Designed to be used as a mixin or parent for repository/data-access classes.
    Provides a single classmethod to safely instantiate model objects and raise
    uniform, informative exceptions on construction errors.

    Attributes:
        model (Type[T]): The SQLAlchemy ORM model class to instantiate.
    """

    model: ModelType

    @classmethod
    def initialize(cls, data: dict, model_name: str) -> T:
        """
        Instantiate a SQLAlchemy model object with error handling.

        :param data: Dict of attributes for the model.
        :param model_name: Name of the model being instantiated (for error reporting).
        :return: The created model instance.
        :raises DataValidationError: If data is invalid.
        :raises UnknownTransactionError: For any other unexpected error.
        """
        try:
            return cls.model(**data)
        except TypeError as exc:
            raise DataValidationError(
                details=f"Invalid argument(s) for model '{model_name}'",
                original=str(exc),
            ) from exc
        except ValueError as exc:
            raise DataValidationError(
                details=f"Invalid value(s) for model '{model_name}'",
                original=str(exc),
            ) from exc
        except Exception as exc:
            raise UnknownTransactionError(
                details=f"Unexpected error while creating '{model_name}'",
                original=str(exc),
            ) from exc
