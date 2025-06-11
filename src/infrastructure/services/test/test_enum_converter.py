from unittest.mock import MagicMock

from src.domain.value_objects import OrderOperation, TimeInForce, OpenClose, DayTrade
from src.infrastructure.services.enum_converter import EnumConverter


def test_enum_converter_to_pfcf_enum():
    mock_exchange_api = MagicMock()
    # side enum
    mock_exchange_api.trade.SideEnum.Buy = "buy"
    mock_exchange_api.trade.SideEnum.Sell = "sell"
    # time in force enum
    mock_exchange_api.trade.TimeInForceEnum.ROD = "ROD"
    mock_exchange_api.trade.TimeInForceEnum.IOC = "IOC"
    mock_exchange_api.trade.TimeInForceEnum.FOK = "FOK"
    # open close enum
    mock_exchange_api.trade.OpenCloseEnum.Y = "Y"
    mock_exchange_api.trade.OpenCloseEnum.N = "N"
    mock_exchange_api.trade.OpenCloseEnum.AUTO = "AUTO"
    # day trade enum
    mock_exchange_api.trade.DayTradeEnum.Y = "Y"
    mock_exchange_api.trade.DayTradeEnum.N = "N"

    enum_converter = EnumConverter(mock_exchange_api)

    # side enum test
    assert enum_converter.to_pfcf_enum(OrderOperation.BUY) == mock_exchange_api.trade.SideEnum.Buy
    assert enum_converter.to_pfcf_enum(OrderOperation.SELL) == mock_exchange_api.trade.SideEnum.Sell
    # time in force enum test
    assert enum_converter.to_pfcf_enum(TimeInForce.ROD) == mock_exchange_api.trade.TimeInForceEnum.ROD
    assert enum_converter.to_pfcf_enum(TimeInForce.IOC) == mock_exchange_api.trade.TimeInForceEnum.IOC
    assert enum_converter.to_pfcf_enum(TimeInForce.FOK) == mock_exchange_api.trade.TimeInForceEnum.FOK
    # open close enum test
    assert enum_converter.to_pfcf_enum(OpenClose.OPEN) == mock_exchange_api.trade.OpenCloseEnum.Y
    assert enum_converter.to_pfcf_enum(OpenClose.CLOSE) == mock_exchange_api.trade.OpenCloseEnum.N
    assert enum_converter.to_pfcf_enum(OpenClose.AUTO) == mock_exchange_api.trade.OpenCloseEnum.AUTO
    # day trade enum test
    assert enum_converter.to_pfcf_enum(DayTrade.Yes) == mock_exchange_api.trade.DayTradeEnum.Y
    assert enum_converter.to_pfcf_enum(DayTrade.No) == mock_exchange_api.trade.DayTradeEnum.N
    # invalid enum test
    assert enum_converter.to_pfcf_enum("test") is None


def test_enum_converter_to_pfcf_decimal():
    mock_exchange_api = MagicMock()
    mock_exchange_api.decimal.Parse = MagicMock()
    mock_exchange_api.decimal.Parse.return_value = 100

    enum_converter = EnumConverter(mock_exchange_api)

    assert enum_converter.to_pfcf_decimal(100) == 100
    mock_exchange_api.decimal.Parse.assert_called_once_with("100")
