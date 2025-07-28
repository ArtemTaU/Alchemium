"""
session.py

This module implements the Unit of Work pattern for asynchronous SQLAlchemy sessions.

Key features:
    - Centralized management of async database sessions and transactions.
    - Explicit commit and rollback handling with custom exception translation.
    - Designed to be used with 'async with' for safe and automatic transaction boundaries.
    - Suitable for working with repository patterns and batch/bulk operations.
"""

from contextlib import AbstractAsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError

from ..errors import (
    UniqueViolation,
    ForeignKeyViolation,
    DataValidationError,
    TransactionError,
    UnknownTransactionError,
    IntegrityErrorMapper,
)


class UnitOfWork(AbstractAsyncContextManager):
    """
    Async Unit of Work for SQLAlchemy sessions.

    Handles session/transaction lifecycle for one business operation.

    Args:
        session_factory (async_sessionmaker): Factory for creating AsyncSession instances.

    Attributes:
        session (AsyncSession): The current database session within the Unit of Work.

    Usage:
        async with UnitOfWork(session_factory) as uow:
            # Use uow.session for all DB operations within this transaction
            ...

    Raises:
        UniqueViolation: If a unique constraint is violated on commit.
        ForeignKeyViolation: If a foreign key constraint is violated on commit.
        DataValidationError: If provided data is invalid for the model.
        CreateError: For generic integrity errors.
        TransactionError: For other SQLAlchemy transaction errors.
        UnknownCreateError: For any other unexpected errors during commit.
    """

    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.session.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()

    async def commit(self):
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            msg = str(exc.orig).lower()
            if "unique" in msg:
                raise UniqueViolation(original=str(exc)) from exc
            if "foreign key" in msg:
                raise ForeignKeyViolation(original=str(exc)) from exc
            raise TransactionError(original=str(exc)) from exc
        except DataError as exc:
            await self.session.rollback()
            raise DataValidationError(original=str(exc)) from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise TransactionError(original=str(exc)) from exc
        except Exception as exc:
            await self.session.rollback()
            raise UnknownTransactionError(details="", original=str(exc)) from exc

    async def rollback(self):
        await self.session.rollback()
