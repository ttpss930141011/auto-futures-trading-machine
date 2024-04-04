""" Module for Value Objects
"""
import enum
import uuid

ConditionId = uuid.UUID


@enum.unique
class OrderOperation(enum.Enum):
    """Enumeration for order operations."""

    BUY = "buy"
    SELL = "sell"

    def __str__(self):
        return {
            OrderOperation.BUY: "buy",
            OrderOperation.SELL: "sell",
        }[self]


@enum.unique
class OrderTypeEnum(enum.Enum):
    """Enumeration for order type."""

    Limit = "Limit"
    Market = "Market"
    MarketPrice = "MarketPrice"  # 範圍市價

    def __str__(self):
        return {
            OrderTypeEnum.Limit: "Limit",
            OrderTypeEnum.Market: "Market",
            OrderTypeEnum.MarketPrice: "MarketPrice",
        }[self]


@enum.unique
class TimeInForce(enum.Enum):
    """Enumeration for time in force."""

    ROD = "ROD"
    IOC = "IOC"
    FOK = "FOK"

    def __str__(self):
        return {
            TimeInForce.ROD: "ROD",
            TimeInForce.IOC: "IOC",
            TimeInForce.FOK: "FOK",
        }[self]


@enum.unique
class OpenClose(enum.Enum):
    """Enumeration for open close."""

    OPEN = "Y"
    CLOSE = "N"
    AUTO = "AUTO"

    def __str__(self):
        return {
            OpenClose.OPEN: "Y",
            OpenClose.CLOSE: "N",
            OpenClose.AUTO: "AUTO",
        }[self]


@enum.unique
class DayTrade(enum.Enum):
    """Enumeration for daily trade."""

    Yes = "Y"
    No = "N"

    def __str__(self):
        return {
            DayTrade.Yes: "Y",
            DayTrade.No: "N",
        }[self]
