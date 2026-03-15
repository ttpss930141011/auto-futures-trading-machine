"""Enum converter for exchange API types.

This module provides conversion between application enums and exchange-specific enums,
following the Single Responsibility Principle.
"""

from src.domain.interfaces.exchange_api import ExchangeApiInterface
from src.domain.value_objects import OrderOperation, TimeInForce, OpenClose, DayTrade, OrderTypeEnum


class EnumConverter:
    """Converts between application enums and exchange API enums.

    This class follows the Single Responsibility Principle by focusing
    solely on enum conversion operations.
    """

    def __init__(self, exchange_api: ExchangeApiInterface) -> None:
        """Initialize the enum converter.

        Args:
            exchange_api: Exchange API interface for accessing enum types.
        """
        self.exchange_api = exchange_api

    def to_pfcf_enum(self, enum):
        """Convert application enum to exchange-specific enum.

        Args:
            enum: Application enum to convert.

        Returns:
            Corresponding exchange enum, or None if not found.
        """
        return self.exchange_api.convert_enum(enum)

    def to_pfcf_decimal(self, value: float):
        """Convert float value to exchange-specific decimal.

        Args:
            value: Float value to convert.

        Returns:
            Exchange decimal representation.
        """
        return self.exchange_api.parse_decimal(value)
