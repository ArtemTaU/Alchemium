import pytest
from src.exceptions import RepositoryUsageError
from tests.models import DummyModel, DummyRepository, IncompleteRepository


@pytest.mark.asyncio
async def test_delete_successfully_calls_session_delete(mock_session):
    obj = DummyModel(name="Test Name")
    await DummyRepository.delete(mock_session, obj)
    mock_session.delete.assert_awaited_once_with(obj)


@pytest.mark.asyncio
async def test_delete_raises_if_model_not_defined(mock_session):
    obj = DummyModel(name="Test Name")

    with pytest.raises(RepositoryUsageError):
        await IncompleteRepository.delete(mock_session, obj)


@pytest.mark.asyncio
async def test_delete_raises_if_object_is_none(mock_session):
    with pytest.raises(RepositoryUsageError):
        await DummyRepository.delete(mock_session, None)


@pytest.mark.asyncio
async def test_delete_does_not_commit_session(mock_session):
    obj = DummyModel(name="Test Name")

    await DummyRepository.delete(mock_session, obj)

    assert not mock_session.commit.called
    assert not mock_session.flush.called


@pytest.mark.asyncio
async def test_delete_raises_if_object_is_not_instance_of_model(mock_session):
    class OtherModel:
        pass

    obj = OtherModel()

    with pytest.raises(RepositoryUsageError) as exc_info:
        await DummyRepository.delete(mock_session, obj)

    assert "Expected instance of 'DummyModel'" in str(exc_info.value)
