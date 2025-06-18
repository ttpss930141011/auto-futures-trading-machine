"""Exchange Event Interface - Abstract interface for exchange event handling."""

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


class EventType(Enum):
    """Standard event types across all exchanges."""
    
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    ERROR = "error"
    
    # Market data events
    TICK_DATA = "tick_data"
    BID_ASK_DATA = "bid_ask_data"
    MARKET_DEPTH = "market_depth"
    
    # Trading events
    ORDER_ACCEPTED = "order_accepted"
    ORDER_REJECTED = "order_rejected"
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_UPDATE = "order_update"
    
    # Account events
    POSITION_UPDATE = "position_update"
    BALANCE_UPDATE = "balance_update"
    MARGIN_UPDATE = "margin_update"


@dataclass
class Event:
    """Base event class."""
    
    event_type: EventType
    timestamp: str
    data: Dict[str, Any]
    source: str  # Exchange name
    error: Optional[str] = None


@dataclass
class TickEvent(Event):
    """Market tick data event."""
    
    symbol: str = ""
    price: float = 0.0
    volume: int = 0
    bid: float = 0.0
    ask: float = 0.0
    bid_volume: int = 0
    ask_volume: int = 0
    
    def __post_init__(self):
        self.event_type = EventType.TICK_DATA


@dataclass
class OrderEvent(Event):
    """Order-related event."""
    
    order_id: str = ""
    account: str = ""
    symbol: str = ""
    side: str = ""
    quantity: int = 0
    price: float = 0.0
    status: str = ""
    
    def __post_init__(self):
        # Set event_type based on status
        status_map = {
            "accepted": EventType.ORDER_ACCEPTED,
            "rejected": EventType.ORDER_REJECTED,
            "filled": EventType.ORDER_FILLED,
            "cancelled": EventType.ORDER_CANCELLED,
        }
        self.event_type = status_map.get(self.status, EventType.ORDER_UPDATE)


@dataclass
class PositionEvent(Event):
    """Position update event."""
    
    account: str = ""
    symbol: str = ""
    quantity: int = 0
    side: str = ""
    average_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    
    def __post_init__(self):
        self.event_type = EventType.POSITION_UPDATE


class ExchangeEventHandlerInterface(ABC):
    """Interface for handling exchange events."""
    
    @abstractmethod
    def on_event(self, event: Event) -> None:
        """Handle any event."""
        pass
    
    @abstractmethod
    def on_tick(self, tick: TickEvent) -> None:
        """Handle tick data."""
        pass
    
    @abstractmethod
    def on_order(self, order: OrderEvent) -> None:
        """Handle order updates."""
        pass
    
    @abstractmethod
    def on_position(self, position: PositionEvent) -> None:
        """Handle position updates."""
        pass
    
    @abstractmethod
    def on_error(self, error: Event) -> None:
        """Handle errors."""
        pass


class ExchangeEventManagerInterface(ABC):
    """Interface for managing exchange event subscriptions."""
    
    @abstractmethod
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle the event
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Callback function to remove
        """
        pass
    
    @abstractmethod
    def subscribe_all(self, handler: ExchangeEventHandlerInterface) -> None:
        """Subscribe to all events with a handler interface.
        
        Args:
            handler: Handler implementing ExchangeEventHandlerInterface
        """
        pass
    
    @abstractmethod
    def unsubscribe_all(self, handler: ExchangeEventHandlerInterface) -> None:
        """Unsubscribe handler from all events.
        
        Args:
            handler: Handler to remove from all subscriptions
        """
        pass
    
    @abstractmethod
    def emit(self, event: Event) -> None:
        """Emit an event to all subscribers.
        
        Args:
            event: Event to emit
        """
        pass