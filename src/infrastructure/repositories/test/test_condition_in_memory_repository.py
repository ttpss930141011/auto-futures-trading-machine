# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from src.infrastructure.repositories.condition_in_memory_repository import ConditionInMemoryRepository


def test_condition_in_memory_repository(fixture_create_condition):
    repository = ConditionInMemoryRepository()
    condition = repository.create(
        action=fixture_create_condition["action"],
        trigger_price=fixture_create_condition["trigger_price"],
        turning_point=fixture_create_condition["turning_point"],
        quantity=fixture_create_condition["quantity"],
        take_profit_point=fixture_create_condition["take_profit_point"],
        stop_loss_point=fixture_create_condition["stop_loss_point"],
        is_following=fixture_create_condition["is_following"]
    )
    response = repository.get(condition.condition_id)
    assert response.condition_id == condition.condition_id
    assert response.action == fixture_create_condition["action"]
    assert response.trigger_price == fixture_create_condition["trigger_price"]
    assert response.turning_point == fixture_create_condition["turning_point"]
    assert response.quantity == fixture_create_condition["quantity"]
    assert response.take_profit_point == fixture_create_condition["take_profit_point"]
    assert response.stop_loss_point == fixture_create_condition["stop_loss_point"]

    response_all = repository.get_all()
    assert len(response_all) == 1

    response_search = repository.search_by_trigger_price(fixture_create_condition["trigger_price"])
    assert len(response_search) == 1

    response_delete = repository.delete(condition.condition_id)
    assert response_delete is True

    response_get = repository.get(condition_id=condition.condition_id)

    assert response_get is None
