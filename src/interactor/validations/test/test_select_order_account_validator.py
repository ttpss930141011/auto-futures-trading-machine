# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


import pytest

from src.interactor.validations.select_order_account_validator import SelectOrderAccountInputDtoValidator


def test_select_order_account_validator_valid_data(
        mocker,
        fixture_select_order_account
):
    mocker.patch("src.interactor.validations.base_input_validator.BaseInputValidator.verify")
    input_data = {
        "index": fixture_select_order_account["index"],
        "order_account": fixture_select_order_account["order_account"],
    }
    schema = {
        "index": {
            "type": "integer",
            "required": True,
            "empty": False
        },
        "order_account": {
            "type": "string",
            "required": True,
            "empty": False
        }
    }
    validator = SelectOrderAccountInputDtoValidator(input_data)
    validator.validate()
    validator.verify.assert_called_once_with(schema)  # pylint: disable=E1101


def test_select_order_account_validator_empty_input(fixture_select_order_account):
    # We are doing just a simple test as the complete test is done in
    # test_base_input_validator.py
    input_data = {
        "index": None,
        "order_account": None,
    }
    validator = SelectOrderAccountInputDtoValidator(input_data)
    with pytest.raises(ValueError) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Index: null value not allowed\nOrder_account: null value not allowed"
