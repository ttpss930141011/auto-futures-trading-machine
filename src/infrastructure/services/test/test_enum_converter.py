from src.domain.value_objects import OrderOperation, TimeInForce, OpenClose, DayTrade
from src.infrastructure.services.enum_converter import EnumConverter


def test_enum_converter_to_pfcf_enum(mocker):
    mock_config = mocker.MagicMock()
    # side enum
    mock_config.EXCHANGE_TRADE.SideEnum.Buy = "buy"
    mock_config.EXCHANGE_TRADE.SideEnum.Sell = "sell"
    # time in force enum
    mock_config.EXCHANGE_TRADE.TimeInForceEnum.ROD = "ROD"
    mock_config.EXCHANGE_TRADE.TimeInForceEnum.IOC = "IOC"
    mock_config.EXCHANGE_TRADE.TimeInForceEnum.FOK = "FOK"
    # open close enum
    mock_config.EXCHANGE_TRADE.OpenCloseEnum.Y = "Y"
    mock_config.EXCHANGE_TRADE.OpenCloseEnum.N = "N"
    mock_config.EXCHANGE_TRADE.OpenCloseEnum.AUTO = "AUTO"
    # day trade enum
    mock_config.EXCHANGE_TRADE.DayTradeEnum.Y = "Y"
    mock_config.EXCHANGE_TRADE.DayTradeEnum.N = "N"

    enum_converter = EnumConverter(mock_config)

    # side enum test
    assert enum_converter.to_pfcf_enum(OrderOperation.BUY) == mock_config.EXCHANGE_TRADE.SideEnum.Buy
    assert enum_converter.to_pfcf_enum(OrderOperation.SELL) == mock_config.EXCHANGE_TRADE.SideEnum.Sell
    # time in force enum test
    assert enum_converter.to_pfcf_enum(TimeInForce.ROD) == mock_config.EXCHANGE_TRADE.TimeInForceEnum.ROD
    assert enum_converter.to_pfcf_enum(TimeInForce.IOC) == mock_config.EXCHANGE_TRADE.TimeInForceEnum.IOC
    assert enum_converter.to_pfcf_enum(TimeInForce.FOK) == mock_config.EXCHANGE_TRADE.TimeInForceEnum.FOK
    # open close enum test
    assert enum_converter.to_pfcf_enum(OpenClose.OPEN) == mock_config.EXCHANGE_TRADE.OpenCloseEnum.Y
    assert enum_converter.to_pfcf_enum(OpenClose.CLOSE) == mock_config.EXCHANGE_TRADE.OpenCloseEnum.N
    assert enum_converter.to_pfcf_enum(OpenClose.AUTO) == mock_config.EXCHANGE_TRADE.OpenCloseEnum.AUTO
    # day trade enum test
    assert enum_converter.to_pfcf_enum(DayTrade.Yes) == mock_config.EXCHANGE_TRADE.DayTradeEnum.Y
    assert enum_converter.to_pfcf_enum(DayTrade.No) == mock_config.EXCHANGE_TRADE.DayTradeEnum.N
    # invalid enum test
    assert enum_converter.to_pfcf_enum("test") is None


def test_enum_converter_to_pfcf_decimal(mocker):
    mock_config = mocker.MagicMock()
    mock_config.EXCHANGE_DECIMAL.Parse = mocker.MagicMock()
    mock_config.EXCHANGE_DECIMAL.Parse.return_value = 0.1

    enum_converter = EnumConverter(mock_config)

    assert enum_converter.to_pfcf_decimal(0.1) == 0.1
    mock_config.EXCHANGE_DECIMAL.Parse.assert_called_once_with("0.1")
