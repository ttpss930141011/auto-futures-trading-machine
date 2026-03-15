from unittest.mock import MagicMock

from src.domain.value_objects import OrderOperation, TimeInForce, OpenClose, DayTrade
from src.infrastructure.services.enum_converter import EnumConverter


def test_enum_converter_to_pfcf_enum():
    mock_exchange_api = MagicMock()

    # Setup convert_enum to return predictable values based on input
    enum_map = {
        OrderOperation.BUY: "buy",
        OrderOperation.SELL: "sell",
        TimeInForce.ROD: "ROD",
        TimeInForce.IOC: "IOC",
        TimeInForce.FOK: "FOK",
        OpenClose.OPEN: "Y",
        OpenClose.CLOSE: "N",
        OpenClose.AUTO: "AUTO",
        DayTrade.Yes: "Y",
        DayTrade.No: "N",
    }
    mock_exchange_api.convert_enum.side_effect = lambda e: enum_map.get(e, None)

    enum_converter = EnumConverter(mock_exchange_api)

    # side enum test
    assert enum_converter.to_pfcf_enum(OrderOperation.BUY) == "buy"
    assert enum_converter.to_pfcf_enum(OrderOperation.SELL) == "sell"
    # time in force enum test
    assert enum_converter.to_pfcf_enum(TimeInForce.ROD) == "ROD"
    assert enum_converter.to_pfcf_enum(TimeInForce.IOC) == "IOC"
    assert enum_converter.to_pfcf_enum(TimeInForce.FOK) == "FOK"
    # open close enum test
    assert enum_converter.to_pfcf_enum(OpenClose.OPEN) == "Y"
    assert enum_converter.to_pfcf_enum(OpenClose.CLOSE) == "N"
    assert enum_converter.to_pfcf_enum(OpenClose.AUTO) == "AUTO"
    # day trade enum test
    assert enum_converter.to_pfcf_enum(DayTrade.Yes) == "Y"
    assert enum_converter.to_pfcf_enum(DayTrade.No) == "N"
    # invalid enum test
    assert enum_converter.to_pfcf_enum("test") is None


def test_enum_converter_to_pfcf_decimal():
    mock_exchange_api = MagicMock()
    mock_exchange_api.parse_decimal.return_value = 100

    enum_converter = EnumConverter(mock_exchange_api)

    assert enum_converter.to_pfcf_decimal(100) == 100
    mock_exchange_api.parse_decimal.assert_called_once_with(100)
