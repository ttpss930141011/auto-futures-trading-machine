"""Exchange API Interface.

This module defines the abstract interface for exchange operations,
following the Dependency Inversion Principle by defining contracts
at the domain layer that infrastructure adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, TYPE_CHECKING

from src.domain.value_objects import (
    OrderOperation,
    OrderTypeEnum,
    TimeInForce,
    OpenClose,
    DayTrade,
)

if TYPE_CHECKING:
    from src.interactor.dtos.send_market_order_dtos import SendMarketOrderOutputDto
    from src.interactor.dtos.get_position_dtos import PositionDto


class ExchangeApiInterface(ABC):
    """Abstract interface for exchange API operations.

    This interface abstracts exchange-specific implementations,
    allowing the core domain to work with any exchange adapter
    that implements these operations.
    """

    @abstractmethod
    def connect(self, **credentials) -> bool:
        """Connect to the exchange with provided credentials.

        Args:
            **credentials: Exchange-specific connection credentials.

        Returns:
            True if connection successful, False otherwise.
        """
        pass

    @abstractmethod
    def send_order(
        self,
        order_account: str,
        item_code: str,
        side: OrderOperation,
        order_type: OrderTypeEnum,
        price: float,
        quantity: int,
        open_close: OpenClose,
        note: str,
        day_trade: DayTrade,
        time_in_force: TimeInForce,
    ) -> "SendMarketOrderOutputDto":
        """Send an order to the exchange.

        Args:
            order_account: Trading account identifier.
            item_code: Product/commodity code.
            side: Buy or sell operation.
            order_type: Market, limit, or market price order.
            price: Order price.
            quantity: Order quantity.
            open_close: Open or close position.
            note: Order note/reference.
            day_trade: Day trade flag.
            time_in_force: Time in force setting.

        Returns:
            SendMarketOrderOutputDto with execution result.
        """
        pass

    @abstractmethod
    def get_positions(self, account: str, product_id: str = "") -> List["PositionDto"]:
        """Get positions for an account.

        Args:
            account: Trading account identifier.
            product_id: Optional product filter, empty string for all.

        Returns:
            List of position DTOs.
        """
        pass

    @abstractmethod
    def subscribe_market_data(self, commodity_id: str, callback: Callable) -> bool:
        """Subscribe to market data for a commodity.

        Args:
            commodity_id: Commodity/product identifier.
            callback: Callback function for market data events.

        Returns:
            True if subscription successful, False otherwise.
        """
        pass

    @abstractmethod
    def convert_enum(self, domain_enum: Any) -> Any:
        """Convert domain enum to exchange-specific enum.

        Args:
            domain_enum: Domain layer enumeration value.

        Returns:
            Exchange-specific enum value.
        """
        pass

    @abstractmethod
    def parse_decimal(self, value: float) -> Any:
        """Parse float value to exchange-specific decimal format.

        Args:
            value: Float value to convert.

        Returns:
            Exchange-specific decimal representation.
        """
        pass

    @abstractmethod
    def get_client(self) -> Any:
        """Get the underlying exchange client object.

        Returns:
            Exchange client implementation.

        Note:
            This is provided for infrastructure-layer components
            that need direct access to exchange-specific features.
            Domain/interactor layers should not use this.
        """
        pass

    @abstractmethod
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for exchange events.

        Args:
            event_type: Type of event to subscribe to.
            callback: Callback function to register.
        """
        pass
