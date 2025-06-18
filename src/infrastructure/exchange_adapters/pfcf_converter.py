"""PFCF Converter Implementation - Converts between internal and PFCF formats."""

from decimal import Decimal
from typing import Any

from src.domain.interfaces.exchange_converter_interface import ExchangeConverterInterface
from src.domain.value_objects import OrderOperation, OrderTypeEnum, OpenClose, DayTrade, TimeInForce


class PFCFConverter(ExchangeConverterInterface):
    """PFCF-specific data format converter."""
    
    def convert_side(self, side: OrderOperation) -> str:
        """Convert internal side to PFCF format."""
        return "0" if side == OrderOperation.BUY else "1"
    
    def convert_side_back(self, exchange_side: Any) -> OrderOperation:
        """Convert PFCF side to internal format."""
        return OrderOperation.BUY if str(exchange_side) == "0" else OrderOperation.SELL
    
    def convert_order_type(self, order_type: OrderTypeEnum) -> str:
        """Convert internal order type to PFCF format."""
        order_type_map = {
            OrderTypeEnum.Limit: "0",
            OrderTypeEnum.Market: "1",
            OrderTypeEnum.Stop: "2",
            OrderTypeEnum.StopLimit: "3",
        }
        return order_type_map.get(order_type, "1")  # Default to market
    
    def convert_order_type_back(self, exchange_order_type: Any) -> OrderTypeEnum:
        """Convert PFCF order type to internal format."""
        order_type_map = {
            "0": OrderTypeEnum.Limit,
            "1": OrderTypeEnum.Market,
            "2": OrderTypeEnum.Stop,
            "3": OrderTypeEnum.StopLimit,
        }
        return order_type_map.get(str(exchange_order_type), OrderTypeEnum.Market)
    
    def convert_time_in_force(self, tif: TimeInForce) -> str:
        """Convert internal time-in-force to PFCF format."""
        tif_map = {
            TimeInForce.IOC: "0",
            TimeInForce.FOK: "1",
            TimeInForce.GTC: "2",
        }
        return tif_map.get(tif, "0")  # Default to IOC
    
    def convert_time_in_force_back(self, exchange_tif: Any) -> TimeInForce:
        """Convert PFCF time-in-force to internal format."""
        tif_map = {
            "0": TimeInForce.IOC,
            "1": TimeInForce.FOK,
            "2": TimeInForce.GTC,
        }
        return tif_map.get(str(exchange_tif), TimeInForce.IOC)
    
    def convert_open_close(self, open_close: OpenClose) -> str:
        """Convert internal open/close to PFCF format."""
        open_close_map = {
            OpenClose.AUTO: "0",
            OpenClose.OPEN: "1",
            OpenClose.CLOSE: "2",
        }
        return open_close_map.get(open_close, "0")  # Default to AUTO
    
    def convert_open_close_back(self, exchange_open_close: Any) -> OpenClose:
        """Convert PFCF open/close to internal format."""
        open_close_map = {
            "0": OpenClose.AUTO,
            "1": OpenClose.OPEN,
            "2": OpenClose.CLOSE,
        }
        return open_close_map.get(str(exchange_open_close), OpenClose.AUTO)
    
    def convert_day_trade(self, day_trade: DayTrade) -> str:
        """Convert internal day trade flag to PFCF format."""
        return "1" if day_trade == DayTrade.Yes else "0"
    
    def convert_day_trade_back(self, exchange_day_trade: Any) -> DayTrade:
        """Convert PFCF day trade flag to internal format."""
        return DayTrade.Yes if str(exchange_day_trade) == "1" else DayTrade.No
    
    def format_price(self, price: float, symbol: str) -> str:
        """Format price for PFCF."""
        # PFCF expects string with specific decimal handling
        if price == 0:
            return "0"  # Market order
        return str(Decimal(str(price)).quantize(Decimal('0.01')))
    
    def format_quantity(self, quantity: int, symbol: str) -> str:
        """Format quantity for PFCF."""
        # PFCF expects string
        return str(quantity)
    
    def convert_error_code(self, exchange_error: Any) -> str:
        """Convert PFCF error code to standardized format."""
        # Map PFCF-specific error codes to standard ones
        error_map = {
            "001": "INSUFFICIENT_BALANCE",
            "002": "INVALID_SYMBOL",
            "003": "MARKET_CLOSED",
            # Add more mappings as needed
        }
        error_str = str(exchange_error)
        return error_map.get(error_str, f"PFCF_ERROR_{error_str}")
    
    def get_converter_name(self) -> str:
        """Get converter name."""
        return "PFCF"