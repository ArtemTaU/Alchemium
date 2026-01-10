from typing import TypeVar, TypeAlias

from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)
ModelType: TypeAlias = type[T]
