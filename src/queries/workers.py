from typing import Any

from sqlalchemy.exc import StatementError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions import QueryExecutionError


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
