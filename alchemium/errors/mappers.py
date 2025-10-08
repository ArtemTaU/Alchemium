from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError
from sqlalchemy.orm.exc import FlushError
from .exceptions import (
    UniqueViolation,
    ForeignKeyViolation,
    TransactionError,
    DataValidationError,
    UnknownTransactionError,
    SessionFlushError,
)


class IntegrityErrorMapper:
    @staticmethod
    def map(exc: IntegrityError) -> Exception:
        msg = str(exc.orig).lower() if exc.orig else str(exc).lower()
        if "unique" in msg:
            return UniqueViolation(original=str(exc))
        if "foreign key" in msg:
            return ForeignKeyViolation(original=str(exc))
        if "not null" in msg or "check constraint" in msg:
            return DataValidationError(original=str(exc))
        return TransactionError(original=str(exc))

    @staticmethod
    def map_general(exc: Exception) -> Exception:
        return TransactionError(original=str(exc))


class ErrorMapper:
    @staticmethod
    def map(exc: Exception) -> Exception:
        match exc:
            case IntegrityError():
                raise IntegrityErrorMapper.map(exc) from exc
            case DataError():
                return DataValidationError(original=str(exc))
            case FlushError():
                return SessionFlushError(original=str(exc))
            case SQLAlchemyError():
                return TransactionError(original=str(exc))
            case _:
                return UnknownTransactionError(details="", original=str(exc))
