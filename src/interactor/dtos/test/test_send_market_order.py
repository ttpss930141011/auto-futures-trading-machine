# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto


def test_send_market_order_input_dto_valid(fixture_send_market_order):
    input_dto = SendMarketOrderInputDto(
        order_account=fixture_send_market_order["order_account"],
        item_code=fixture_send_market_order["item_code"],
        side=fixture_send_market_order["side"],
        order_type=fixture_send_market_order["order_type"],
        price=fixture_send_market_order["price"],
        quantity=fixture_send_market_order["quantity"],
        time_in_force=fixture_send_market_order["time_in_force"],
        open_close=fixture_send_market_order["open_close"],
        note=fixture_send_market_order["note"],
    )

    assert input_dto.order_account == fixture_send_market_order["order_account"]
    assert input_dto.item_code == fixture_send_market_order["item_code"]
    assert input_dto.side == fixture_send_market_order["side"]
    assert input_dto.order_type == fixture_send_market_order["order_type"]
    assert input_dto.price == fixture_send_market_order["price"]
    assert input_dto.quantity == fixture_send_market_order["quantity"]
    assert input_dto.time_in_force == fixture_send_market_order["time_in_force"]
    assert input_dto.open_close == fixture_send_market_order["open_close"]
    assert input_dto.note == fixture_send_market_order["note"]

    assert input_dto.to_dict() == {
        "order_account": fixture_send_market_order["order_account"],
        "item_code": fixture_send_market_order["item_code"],
        "side": fixture_send_market_order["side"].value,
        "order_type": fixture_send_market_order["order_type"].value,
        "price": fixture_send_market_order["price"],
        "quantity": fixture_send_market_order["quantity"],
        "time_in_force": fixture_send_market_order["time_in_force"].value,
        "open_close": fixture_send_market_order["open_close"].value,
        "day_trade": fixture_send_market_order["day_trade"].value,
        "note": fixture_send_market_order["note"],
    }


def test_send_market_order_input_dto_to_pfcf_dict_valid(fixture_send_market_order):
    from unittest.mock import MagicMock, patch
    
    # Create service container mock
    mock_service_container = MagicMock()
    mock_service_container.exchange_api = MagicMock()
    
    with patch("src.interactor.dtos.send_market_order_dtos.EnumConverter") as mock_converter:
        mock_converter_instance = mock_converter.return_value
        mock_converter_instance.to_pfcf_enum.return_value = "Test Enum"
        mock_converter_instance.to_pfcf_decimal.return_value = "Test Decimal"

        input_dto = SendMarketOrderInputDto(
            order_account=fixture_send_market_order["order_account"],
            item_code=fixture_send_market_order["item_code"],
            side=fixture_send_market_order["side"],
            order_type=fixture_send_market_order["order_type"],
            price=fixture_send_market_order["price"],
            quantity=fixture_send_market_order["quantity"],
            time_in_force=fixture_send_market_order["time_in_force"],
            open_close=fixture_send_market_order["open_close"],
            note=fixture_send_market_order["note"],
        )

        pfcf_dict = input_dto.to_pfcf_dict(service_container=mock_service_container)

        mock_converter_instance.to_pfcf_enum.assert_called()
        mock_converter.assert_called_once_with(mock_service_container.exchange_api)
        assert pfcf_dict == {
            "ACTNO": fixture_send_market_order["order_account"],
            "PRODUCTID": fixture_send_market_order["item_code"],
            "BS": "Test Enum",
            "ORDERTYPE": "Test Enum",
            "PRICE": "Test Decimal",
            "ORDERQTY": fixture_send_market_order["quantity"],
            "TIMEINFORCE": "Test Enum",
            "OPENCLOSE": "Test Enum",
            "DTRADE": "Test Enum",
            "NOTE": fixture_send_market_order["note"],
        }
