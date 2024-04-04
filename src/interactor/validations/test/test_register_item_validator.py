# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


import pytest

from src.interactor.validations.register_item_validator import RegisterItemInputDtoValidator


def test_register_item_validator_valid_data(
        mocker,
        fixture_register_item
):
    mocker.patch("src.interactor.validations.base_input_validator.BaseInputValidator.verify")
    input_data = {
        "account": fixture_register_item["account"],
        "item_code": fixture_register_item["item_code"],
    }
    schema = {
        "account": {
            "type": "string",
            "minlength": 11,
            "maxlength": 80,
            "required": True,
            "empty": False
        },
        "item_code": {
            "type": "string",
            "required": True,
            "empty": False
        },
    }
    validator = RegisterItemInputDtoValidator(input_data)
    validator.validate()
    validator.verify.assert_called_once_with(schema)  # pylint: disable=E1101


def test_register_item_validator_empty_input(fixture_register_item):
    # We are doing just a simple test as the complete test is done in
    # test_base_input_validator.py
    input_data = {
        "account": "",
        "item_code": "1234567890",
    }
    validator = RegisterItemInputDtoValidator(input_data)
    with pytest.raises(ValueError) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Account: empty values not allowed"
