# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


import pytest

from src.interactor.validations.user_logout_validator import UserLogoutInputDtoValidator


def test_user_logout_validator_valid_data(
        mocker,
        fixture_user
):
    mocker.patch("src.interactor.validations.base_input_validator.BaseInputValidator.verify")
    input_data = {
        "account": fixture_user["account"],
    }
    schema = {
        "account": {
            "type": "string",
            "minlength": 11,
            "maxlength": 80,
            "required": True,
            "empty": False
        },
    }
    validator = UserLogoutInputDtoValidator(input_data)
    validator.validate()
    validator.verify.assert_called_once_with(schema)  # pylint: disable=E1101


def test_user_logout_validator_empty_input(fixture_user):
    # We are doing just a simple test as the complete test is done in
    # base_input_validator_test.py
    input_data = {
        "account": "",
    }
    validator = UserLogoutInputDtoValidator(input_data)
    with pytest.raises(ValueError) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Account: empty values not allowed"
