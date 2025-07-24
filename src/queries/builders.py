from typing import Optional, List, Dict, Any

from sqlalchemy import Select
from sqlalchemy.exc import InvalidRequestError, ArgumentError
from sqlalchemy.orm import selectinload
from src.exceptions import (
    RelationNotFoundError,
    FieldNotFoundError,
    QueryError,
    OrderByFieldError,
    PaginationParameterError,
    DataValidationError,
    UnknownTransactionError,
)
from src.typing import ModelType, T


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


class QueryBuilder:
    """
    Utility mixin class for building and modifying SQLAlchemy Select statements with
    support for dynamic joins, filters, ordering, and pagination.

    This class is intended to be used as a mixin for repository or data access classes
    that operate with SQLAlchemy ORM models. It provides helper class methods to:
      - Apply selectinload joins for related models via `_apply_joins`
      - Add WHERE conditions based on filters via `_apply_filters`
      - Add ORDER BY clause via `_apply_order_by`
      - Add OFFSET and LIMIT for pagination via `_apply_pagination`

    All methods include error handling with custom exceptions for better diagnostics
    and unified error reporting.

    Attributes:
        model (ModelType): SQLAlchemy ORM model class associated with the query.
    """

    model: ModelType

    @classmethod
    def apply_joins(
        cls,
        stmt: Select,
        joins: Optional[List[str]],
        model_name: str,
    ) -> Select:
        """
        Apply SQLAlchemy selectinload joins to a select statement.

        :param stmt: SQLAlchemy select statement.
        :param joins: List of related fields for joining.
        :param model_name: Name of the ORM model (for error reporting).
        :type stmt: Select
        :type joins: Optional[List[str]]
        :type model_name: str
        :raises RelationNotFoundError: If join attribute not found or invalid.
        :return: Modified select statement with join options.
        :rtype: Select
        """
        if not joins:
            return stmt

        for rel in joins:
            try:
                join_attr = getattr(cls.model, rel)
                stmt = stmt.options(selectinload(join_attr))
            except (AttributeError, InvalidRequestError, ArgumentError) as exc:
                raise RelationNotFoundError(
                    model=model_name,
                    rel=rel,
                    original=f" Original error: {exc}" if exc else "",
                ) from exc
        return stmt

    @classmethod
    def apply_filters(
        cls,
        stmt: Select,
        filters: Optional[Dict[str, Any]],
        model_name: str,
    ) -> Select:
        """
        Apply filters to a select statement.

        :param stmt: SQLAlchemy select statement.
        :param filters: Dictionary of field-value filters.
        :param model_name: Name of the ORM model (for error reporting).
        :type stmt: Select
        :type filters: Optional[Dict[str, Any]]
        :type model_name: str
        :raises FieldNotFoundError: If field is not found in model.
        :raises QueryError: For other unknown filter errors.
        :return: Modified select statement with filter conditions.
        :rtype: Select
        """
        if not filters:
            return stmt

        for k, v in filters.items():
            try:
                attr = getattr(cls.model, k, None)
                if attr is None:
                    raise FieldNotFoundError(
                        model=model_name,
                        field=k,
                        original="",
                    )
                stmt = stmt.where(attr == v)
            except FieldNotFoundError:
                raise
            except AttributeError as exc:
                raise FieldNotFoundError(
                    model=model_name,
                    field=k,
                    original="",
                ) from exc
            except Exception as exc:
                raise QueryError(
                    model=model_name,
                    field=k,
                    original=f" Original error: {exc}" if exc else "",
                ) from exc
        return stmt

    @classmethod
    def apply_order_by(
        cls,
        stmt: Select,
        order_by: Optional[str],
        model_name: str,
    ) -> Select:
        """
        Apply order_by to a select statement.

        :param stmt: SQLAlchemy select statement.
        :param order_by: Field name to order by.
        :param model_name: Name of the ORM model (for error reporting).
        :type stmt: Select
        :type order_by: Optional[str]
        :type model_name: str
        :raises OrderByFieldError: If order_by field is invalid.
        :return: Modified select statement with ordering.
        :rtype: Select
        """
        if not order_by:
            return stmt

        try:
            order_attr = getattr(cls.model, order_by, None)
            if order_attr is None:
                raise OrderByFieldError(
                    model=model_name,
                    field=order_by,
                    original="",
                )
            stmt = stmt.order_by(order_attr)
        except OrderByFieldError:
            raise
        except Exception as exc:
            raise OrderByFieldError(
                model=model_name,
                field=order_by,
                original=f" Original error: {exc}" if exc else "",
            ) from exc
        return stmt

    @classmethod
    def apply_pagination(
        cls,
        stmt: Select,
        skip: Optional[int],
        limit: Optional[int],
        model_name: str,
    ) -> Select:
        """
        Apply skip (offset) and limit to a select statement.

        :param stmt: SQLAlchemy select statement.
        :param skip: Number of records to skip (offset).
        :param limit: Maximum number of records to return.
        :param model_name: Name of the ORM model (for error reporting).
        :type stmt: Select
        :type skip: Optional[int]
        :type limit: Optional[int]
        :type model_name: str
        :raises PaginationParameterError: If skip or limit cause an error.
        :return: Modified select statement with offset/limit.
        :rtype: Select
        """
        if skip is not None:
            try:
                stmt = stmt.offset(skip)
            except Exception as exc:
                raise PaginationParameterError(
                    model=model_name,
                    field="skip",
                    original=f" Original error: {exc}" if exc else "",
                ) from exc
        if limit is not None:
            try:
                stmt = stmt.limit(limit)
            except Exception as exc:
                raise PaginationParameterError(
                    model=model_name,
                    field="limit",
                    original=f" Original error: {exc}" if exc else "",
                ) from exc
        return stmt
