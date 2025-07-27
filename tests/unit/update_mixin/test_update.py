import pytest

from src.exceptions import (
    DataValidationError,
    RepositoryUsageError,
)
from tests.models import DummyModel, DummyRepository, IncompleteRepository


def test_update_successful_attribute_change():
    """
    Test successful all attributes update.
    """
    obj = DummyModel(name="Initial", age=30)
    data = {"name": "Updated", "age": 35}

    DummyRepository.update(obj, data)

    assert obj.name == "Updated"
    assert obj.age == 35


def test_update_partial_attribute_change():
    """
    Test successful partial attributes update.
    """
    obj = DummyModel(name="Initial", age=30)
    data = {"age": 99}

    DummyRepository.update(obj, data)

    assert obj.name == "Initial"
    assert obj.age == 99


def test_update_with_empty_data_does_nothing():
    """
    Test update with empty data.
    """
    obj = DummyModel(name="Initial", age=30)
    data = {}

    DummyRepository.update(obj, data)

    assert obj.name == "Initial"
    assert obj.age == 30


def test_update_raises_on_invalid_field():
    """
    Test raise exception on invalid field.
    """
    obj = DummyModel(name="Initial")
    data = {"nonexistent": "value"}

    with pytest.raises(DataValidationError) as exc_info:
        DummyRepository.update(obj, data)

    assert "nonexistent" in str(exc_info.value)


def test_update_raises_if_model_not_defined():
    """
    Test raise exception for update if the model is not defined.
    """
    obj = DummyModel(name="Initial", age=30)
    data = {"name": "Updated"}

    with pytest.raises(RepositoryUsageError):
        IncompleteRepository.update(obj, data)


def test_update_raises_if_object_is_none():
    """
    Test raise exception for update if object to update is None.
    """
    data = {"name": "Updated"}

    with pytest.raises(RepositoryUsageError):
        DummyRepository.update(None, data)


@pytest.mark.asyncio
async def test_update_raises_if_object_is_not_instance_of_model(mock_session):
    class OtherModel:
        pass

    obj = OtherModel()

    data = {"name": "Updated"}

    with pytest.raises(RepositoryUsageError) as exc_info:
        DummyRepository.update(obj, data)

    assert "Expected instance of 'DummyModel'" in str(exc_info.value)
