# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


import pytest

from src.interactor.validations.create_condition_validator import CreateConditionInputDtoValidator


def test_create_condition_validator_valid_data(
        mocker,
        fixture_create_condition
):
    mocker.patch("src.interactor.validations.base_input_validator.BaseInputValidator.verify")
    input_data = {
        "action": fixture_create_condition["action"],
        "trigger_price": fixture_create_condition["trigger_price"],
        "turning_point": fixture_create_condition["turning_point"],
        "quantity": fixture_create_condition["quantity"],
        "take_profit_point": fixture_create_condition["take_profit_point"],
        "stop_loss_point": fixture_create_condition["stop_loss_point"],
        "is_following": fixture_create_condition["is_following"]
    }
    schema = {
        "action": {
            "type": "string",
            "allowed": ["buy", "sell"],
            "required": True,
            "empty": False
        },
        "trigger_price": {
            "type": "integer",
            "required": True,
            "empty": False
        },
        "turning_point": {
            "type": "integer",
            "required": True,
            "empty": False
        },
        "quantity": {
            "type": "integer",
            "required": True,
            "empty": False
        },
        "take_profit_point": {
            "type": "integer",
            "required": True,
            "empty": False
        },
        "stop_loss_point": {
            "type": "integer",
            "required": True,
            "empty": False
        },
        "is_following": {
            "type": "boolean",
            "required": False,
            "empty": False
        }
    }
    validator = CreateConditionInputDtoValidator(input_data)
    validator.validate()
    validator.verify.assert_called_once_with(schema)  # pylint: disable=E1101


def test_create_condition_validator_empty_input(fixture_create_condition):
    # We are doing just a simple test as the complete test is done in
    # test_base_input_validator.py
    input_data = {
        "action": '123',
        "trigger_price": fixture_create_condition["trigger_price"],
        "turning_point": fixture_create_condition["turning_point"],
        "quantity": fixture_create_condition["quantity"],
        "take_profit_point": fixture_create_condition["take_profit_point"],
        "stop_loss_point": fixture_create_condition["stop_loss_point"],
        "is_following": fixture_create_condition["is_following"]
    }
    validator = CreateConditionInputDtoValidator(input_data)
    with pytest.raises(ValueError) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Action: unallowed value 123"
