from sqlalchemy.exc import IntegrityError
from src.errors import UniqueViolation, ForeignKeyViolation, TransactionError


class IntegrityErrorMapper:
    @staticmethod
    def map(exc: IntegrityError) -> Exception:
        msg = str(exc.orig).lower() if exc.orig else str(exc).lower()
        if "unique" in msg:
            return UniqueViolation(original=str(exc))
        if "foreign key" in msg:
            return ForeignKeyViolation(original=str(exc))
        return TransactionError(original=str(exc))

    @staticmethod
    def map_general(exc: Exception) -> Exception:
        return TransactionError(original=str(exc))
