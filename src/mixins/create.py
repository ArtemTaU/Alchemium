from typing import Type, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..typing import T


class CreateMixin:
    model = None

    @classmethod
    async def create(cls: Type[T], asession: AsyncSession, data: Dict[str, Any]) -> T:
        """
        Create a new record in the database. Does NOT commit!
        Args:
            asession (AsyncSession): Async database session.
            data (dict): Data to create a new record.
        Returns:
            T: The newly created ORM model instance.
        Raises:
            NotImplementedError: If the repository does not define model attribute.
        """
        if cls.model is None:
            raise NotImplementedError(
                f"{cls.__name__}: Repository must define model attribute"
            )
        obj = cls.model(**data)
        asession.add(obj)
        return obj
