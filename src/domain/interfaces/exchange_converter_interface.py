"""Exchange Converter Interface - Abstract interface for data conversion between internal and broker formats."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from enum import Enum

from src.domain.enums import OrderOperation, OrderTypeEnum, OpenClose, DayTrade, TimeInForce


class ExchangeConverterInterface(ABC):
    """Abstract interface for converting between internal and exchange-specific formats."""
    
    @abstractmethod
    def convert_side(self, side: OrderOperation) -> Any:
        """Convert internal side enum to exchange-specific format."""
        pass
    
    @abstractmethod
    def convert_side_back(self, exchange_side: Any) -> OrderOperation:
        """Convert exchange-specific side to internal enum."""
        pass
    
    @abstractmethod
    def convert_order_type(self, order_type: OrderTypeEnum) -> Any:
        """Convert internal order type to exchange-specific format."""
        pass
    
    @abstractmethod
    def convert_order_type_back(self, exchange_order_type: Any) -> OrderTypeEnum:
        """Convert exchange-specific order type to internal enum."""
        pass
    
    @abstractmethod
    def convert_time_in_force(self, tif: TimeInForce) -> Any:
        """Convert internal time-in-force to exchange-specific format."""
        pass
    
    @abstractmethod
    def convert_time_in_force_back(self, exchange_tif: Any) -> TimeInForce:
        """Convert exchange-specific time-in-force to internal enum."""
        pass
    
    @abstractmethod
    def convert_open_close(self, open_close: OpenClose) -> Any:
        """Convert internal open/close to exchange-specific format."""
        pass
    
    @abstractmethod
    def convert_open_close_back(self, exchange_open_close: Any) -> OpenClose:
        """Convert exchange-specific open/close to internal enum."""
        pass
    
    @abstractmethod
    def convert_day_trade(self, day_trade: DayTrade) -> Any:
        """Convert internal day trade flag to exchange-specific format."""
        pass
    
    @abstractmethod
    def convert_day_trade_back(self, exchange_day_trade: Any) -> DayTrade:
        """Convert exchange-specific day trade flag to internal enum."""
        pass
    
    @abstractmethod
    def format_price(self, price: float, symbol: str) -> Any:
        """Format price according to exchange requirements."""
        pass
    
    @abstractmethod
    def format_quantity(self, quantity: int, symbol: str) -> Any:
        """Format quantity according to exchange requirements."""
        pass
    
    @abstractmethod
    def convert_error_code(self, exchange_error: Any) -> str:
        """Convert exchange-specific error code to standardized format."""
        pass
    
    @abstractmethod
    def get_converter_name(self) -> str:
        """Get the name of this converter (e.g., 'PFCF', 'YUANTA')."""
        pass