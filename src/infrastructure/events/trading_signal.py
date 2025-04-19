"""Trading Signal Event Definition."""
from datetime import datetime

from src.domain.value_objects import OrderOperation
from src.infrastructure.events.event import Event


class TradingSignal(Event):
    """Represents a signal to place an order.

    Attributes:
        when: The datetime when the signal was generated.
        operation: The type of order (BUY or SELL).
        commodity_id: The identifier of the commodity to trade.
    """

    def __init__(self, when: datetime, operation: OrderOperation, commodity_id: str):
        """Initializes a TradingSignal.

        Args:
            when: The datetime when the signal was generated.
            operation: The type of order (BUY or SELL).
            commodity_id: The identifier of the commodity to trade.
        """
        super().__init__(when)
        self.operation = operation
        self.commodity_id = commodity_id

    def __repr__(self) -> str:
        """Return a string representation of the TradingSignal."""
        return (
            f"TradingSignal(when={self.when.isoformat()}, "
            f"operation={self.operation.name}, "
            f"commodity_id='{self.commodity_id}')"
        ) 