import uuid
from pathlib import Path

import pytest

from src.infrastructure.repositories.condition_json_file_repository import \
    ConditionJsonFileRepository
from src.domain.value_objects import OrderOperation


@pytest.fixture
def repo_path(tmp_path):
    # Ensure clean temp directory
    return tmp_path / 'conditions.json'


@pytest.fixture
def repo(repo_path):
    # Initialize repository with temp file path
    return ConditionJsonFileRepository(str(repo_path))


def test_create_and_get(repo, repo_path):
    # Initially empty
    assert repo.get_all() == {}
    # Create a condition
    cond = repo.create(
        action=OrderOperation.BUY,
        trigger_price=100,
        turning_point=5,
        quantity=1,
        take_profit_point=10,
        stop_loss_point=3,
        is_following=True,
    )
    # File exists
    assert Path(repo_path).is_file()
    # Retrieved by id
    fetched = repo.get(cond.condition_id)
    assert fetched.condition_id == cond.condition_id
    assert fetched.action == OrderOperation.BUY
    # get_all contains the entry
    all_data = repo.get_all()
    assert cond.condition_id in all_data


def test_search_update_delete(repo):
    # Create two conditions with distinct trigger prices
    c1 = repo.create(OrderOperation.SELL, 50, 1, 2, 5, 2, False)
    c2 = repo.create(OrderOperation.BUY, 75, 2, 3, 8, 4, False)
    # Search by trigger_price
    found = repo.search_by_trigger_price(75)
    assert list(found.keys()) == [c2.condition_id]
    # Update c1 quantity
    c1.quantity = 9
    updated = repo.update(c1)
    assert updated.quantity == 9
    # Delete c2
    deleted = repo.delete(c2.condition_id)
    assert deleted is True
    assert repo.get(c2.condition_id) is None
    # delete non-existing returns False
    assert repo.delete(uuid.uuid4()) is False


def test_delete_all(repo):
    # Create multiple
    repo.create(OrderOperation.BUY, 10, 1, 1, 1, 1, False)
    repo.create(OrderOperation.SELL, 20, 1, 1, 1, 1, False)
    assert repo.get_all()
    # Clear all
    ok = repo.delete_all()
    assert ok is True
    assert repo.get_all() == {}


def test_load_invalid_json(repo_path):
    # Write invalid JSON
    repo_path.write_text('invalid json')
    # Initialize repo should handle decode error gracefully
    repo = ConditionJsonFileRepository(str(repo_path))
    # No exception and empty data store
    assert repo.get_all() == {}
