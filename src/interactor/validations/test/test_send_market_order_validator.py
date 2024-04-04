# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


import pytest

from src.interactor.validations.send_market_order_validator import SendMarketOrderInputDtoValidator


def test_send_market_order_validator_valid_data(
        mocker,
        fixture_send_market_order
):
    mocker.patch("src.interactor.validations.base_input_validator.BaseInputValidator.verify")
    input_data = {
        "order_account": fixture_send_market_order["order_account"],
        "item_code": fixture_send_market_order["item_code"],
        "side": fixture_send_market_order["side"].value,
        "order_type": fixture_send_market_order["order_type"].value,
        "price": fixture_send_market_order["price"],
        "quantity": fixture_send_market_order["quantity"],
        "time_in_force": fixture_send_market_order["time_in_force"].value,
        "open_close": fixture_send_market_order["open_close"].value,
        "day_trade": fixture_send_market_order["day_trade"].value,
        "note": "note"
    }
    schema = {
        "order_account": {
            "type": "string",
            "required": True,
            "empty": False
        },
        "item_code": {
            "type": "string",
            "required": True,
            "empty": False
        },
        "side": {
            "type": "string",
            "allowed": ["buy", "sell"],
            "required": True,
            "empty": False
        },
        "order_type": {
            "type": "string",
            "allowed": ["Limit", "Market", "MarketPrice"],
            "required": True,
            "empty": False
        },
        "price": {
            "type": "float",
            "required": True,
            "empty": False
        },
        "quantity": {
            "type": "integer",
            "required": True,
            "empty": False
        },
        "time_in_force": {
            "type": "string",
            "allowed": ["ROD", "IOC", "FOK"],
            "required": True,
            "empty": False
        },
        "open_close": {
            "type": "string",
            "allowed": ["Y", "N", "AUTO"],
            "required": True,
            "empty": False
        },
        "day_trade": {
            "type": "string",
            "allowed": ["Y", "N"],
            "required": True,
            "empty": False
        },
        "note": {
            "type": "string",
            "minlength": 0,
            "maxlength": 10,
            "required": False,
            "empty": True
        }
    }
    validator = SendMarketOrderInputDtoValidator(input_data)
    validator.validate()
    validator.verify.assert_called_once_with(schema)  # pylint: disable=E1101


def test_send_market_order_validator_empty_input(fixture_send_market_order):
    # We are doing just a simple test as the complete test is done in
    # test_base_input_validator.py
    input_data = {
        "order_account": "",
        "item_code": fixture_send_market_order["item_code"],
        "side": fixture_send_market_order["side"].value,
        "order_type": fixture_send_market_order["order_type"].value,
        "price": fixture_send_market_order["price"],
        "quantity": fixture_send_market_order["quantity"],
        "time_in_force": fixture_send_market_order["time_in_force"].value,
        "open_close": fixture_send_market_order["open_close"].value,
        "day_trade": fixture_send_market_order["day_trade"].value,
        "note": "note"
    }
    validator = SendMarketOrderInputDtoValidator(input_data)
    with pytest.raises(ValueError) as exception_info:
        validator.validate()
    assert str(exception_info.value) == "Order_account: empty values not allowed"
