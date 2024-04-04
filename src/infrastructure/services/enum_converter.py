from src.app.cli_pfcf.config import Config
from src.domain.value_objects import OrderOperation, TimeInForce, OpenClose, DayTrade, OrderTypeEnum


class EnumConverter:

    def __init__(self, config: Config):
        self.config = config

    def to_pfcf_enum(self, enum):

        if isinstance(enum, OrderOperation):
            return {
                OrderOperation.BUY: self.config.EXCHANGE_TRADE.SideEnum.Buy,
                OrderOperation.SELL: self.config.EXCHANGE_TRADE.SideEnum.Sell,
            }[enum]

        elif isinstance(enum, TimeInForce):
            return {
                TimeInForce.ROD: self.config.EXCHANGE_TRADE.TimeInForceEnum.ROD,
                TimeInForce.IOC: self.config.EXCHANGE_TRADE.TimeInForceEnum.IOC,
                TimeInForce.FOK: self.config.EXCHANGE_TRADE.TimeInForceEnum.FOK,
            }[enum]

        elif isinstance(enum, OpenClose):
            return {
                OpenClose.OPEN: self.config.EXCHANGE_TRADE.OpenCloseEnum.Y,
                OpenClose.CLOSE: self.config.EXCHANGE_TRADE.OpenCloseEnum.N,
                OpenClose.AUTO: self.config.EXCHANGE_TRADE.OpenCloseEnum.AUTO,
            }[enum]

        elif isinstance(enum, DayTrade):
            return {
                DayTrade.Yes: self.config.EXCHANGE_TRADE.DayTradeEnum.Y,
                DayTrade.No: self.config.EXCHANGE_TRADE.DayTradeEnum.N,
            }[enum]

        elif isinstance(enum, OrderTypeEnum):
            return {
                OrderTypeEnum.Market: self.config.EXCHANGE_TRADE.OrderTypeEnum.Market,
                OrderTypeEnum.Limit: self.config.EXCHANGE_TRADE.OrderTypeEnum.Limit,
                OrderTypeEnum.MarketPrice: self.config.EXCHANGE_TRADE.OrderTypeEnum.MarketPrice,
            }[enum]
        else:
            return None

    def to_pfcf_decimal(self, value: float):
        return self.config.EXCHANGE_DECIMAL.Parse(str(value))
