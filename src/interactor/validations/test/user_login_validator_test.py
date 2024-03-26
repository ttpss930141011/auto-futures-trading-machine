# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


import pytest

from src.interactor.validations.user_login_validator import UserLoginInputDtoValidator


def test_user_login_validator_valid_data(
        mocker,
        fixture_user
):
    mocker.patch("src.interactor.validations.base_input_validator.BaseInputValidator.verify")
    input_data = {
        "account": fixture_user["account"],
        "password": fixture_user["password"],
        "ip_address": fixture_user["ip_address"]
    }
    schema = {
        "account": {
            "type": "string",
            "minlength": 11,
            "maxlength": 80,
            "required": True,
            "empty": False
        },
        "password": {
            "type": "string",
            "minlength": 5,
            "maxlength": 200,
            "required": True,
            "empty": False
        },
        "ip_address": {
            "type": "string",
            "minlength": 5,
            "maxlength": 200,
            "required": True,
            "empty": False
        }
    }
    validator = UserLoginInputDtoValidator(input_data)
    validator.validate()
    validator.verify.assert_called_once_with(schema)  # pylint: disable=E1101


def test_user_login_validator_empty_input(fixture_user):
    # We are doing just a simple test as the complete test is done in
    # base_input_validator_test.py
    input_data = {
        "account": fixture_user["account"],
        "password": "",
        "ip_address": fixture_user["ip_address"]
    }
    validator = UserLoginInputDtoValidator(input_data)
    with pytest.raises(ValueError) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Password: empty values not allowed"
