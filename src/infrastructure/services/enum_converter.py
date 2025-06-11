"""Enum converter for PFCF API types.

This module provides conversion between application enums and PFCF API enums,
following the Single Responsibility Principle.
"""

from src.infrastructure.pfcf_client.api import PFCFApi
from src.domain.value_objects import OrderOperation, TimeInForce, OpenClose, DayTrade, OrderTypeEnum


class EnumConverter:
    """Converts between application enums and PFCF API enums.
    
    This class follows the Single Responsibility Principle by focusing
    solely on enum conversion operations.
    """
    
    def __init__(self, exchange_api: PFCFApi) -> None:
        """Initialize the enum converter.
        
        Args:
            exchange_api: PFCF API instance for accessing enum types.
        """
        self.exchange_api = exchange_api

    def to_pfcf_enum(self, enum):
        """Convert application enum to PFCF API enum.
        
        Args:
            enum: Application enum to convert.
            
        Returns:
            Corresponding PFCF API enum, or None if not found.
        """
        if isinstance(enum, OrderOperation):
            return {
                OrderOperation.BUY: self.exchange_api.trade.SideEnum.Buy,
                OrderOperation.SELL: self.exchange_api.trade.SideEnum.Sell,
            }[enum]

        elif isinstance(enum, TimeInForce):
            return {
                TimeInForce.ROD: self.exchange_api.trade.TimeInForceEnum.ROD,
                TimeInForce.IOC: self.exchange_api.trade.TimeInForceEnum.IOC,
                TimeInForce.FOK: self.exchange_api.trade.TimeInForceEnum.FOK,
            }[enum]

        elif isinstance(enum, OpenClose):
            return {
                OpenClose.OPEN: self.exchange_api.trade.OpenCloseEnum.Y,
                OpenClose.CLOSE: self.exchange_api.trade.OpenCloseEnum.N,
                OpenClose.AUTO: self.exchange_api.trade.OpenCloseEnum.AUTO,
            }[enum]

        elif isinstance(enum, DayTrade):
            return {
                DayTrade.Yes: self.exchange_api.trade.DayTradeEnum.Y,
                DayTrade.No: self.exchange_api.trade.DayTradeEnum.N,
            }[enum]

        elif isinstance(enum, OrderTypeEnum):
            return {
                OrderTypeEnum.Market: self.exchange_api.trade.OrderTypeEnum.Market,
                OrderTypeEnum.Limit: self.exchange_api.trade.OrderTypeEnum.Limit,
                OrderTypeEnum.MarketPrice: self.exchange_api.trade.OrderTypeEnum.MarketPrice,
            }[enum]
        else:
            return None

    def to_pfcf_decimal(self, value: float):
        """Convert float value to PFCF decimal.
        
        Args:
            value: Float value to convert.
            
        Returns:
            PFCF decimal representation.
        """
        return self.exchange_api.decimal.Parse(str(value))
