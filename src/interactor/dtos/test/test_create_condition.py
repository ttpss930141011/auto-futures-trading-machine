# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.interactor.dtos.create_condition_dtos import CreateConditionInputDto


def test_create_condition_input_dto_valid(fixture_create_condition):
    input_dto = CreateConditionInputDto(
        action=fixture_create_condition["action"],
        trigger_price=fixture_create_condition["trigger_price"],
        turning_point=fixture_create_condition["turning_point"],
        quantity=fixture_create_condition["quantity"],
        take_profit_point=fixture_create_condition["take_profit_point"],
        stop_loss_point=fixture_create_condition["stop_loss_point"],
        is_following=fixture_create_condition["is_following"]
    )

    assert input_dto.action == fixture_create_condition["action"]
    assert input_dto.trigger_price == fixture_create_condition["trigger_price"]
    assert input_dto.to_dict() == {
        "action": fixture_create_condition["action"],
        "trigger_price": fixture_create_condition["trigger_price"],
        "turning_point": fixture_create_condition["turning_point"],
        "quantity": fixture_create_condition["quantity"],
        "take_profit_point": fixture_create_condition["take_profit_point"],
        "stop_loss_point": fixture_create_condition["stop_loss_point"],
        "is_following": fixture_create_condition["is_following"]
    }
