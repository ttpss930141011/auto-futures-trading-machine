"""Exchange Event Manager - Generic implementation of event management."""

from typing import Callable, Dict, List, Set
from collections import defaultdict
import logging
import threading

from src.domain.interfaces.exchange_event_interface import (
    ExchangeEventManagerInterface,
    ExchangeEventHandlerInterface,
    Event,
    EventType,
    TickEvent,
    OrderEvent,
    PositionEvent
)


class ExchangeEventManager(ExchangeEventManagerInterface):
    """Generic event manager implementation."""
    
    def __init__(self, exchange_name: str):
        """Initialize event manager.
        
        Args:
            exchange_name: Name of the exchange for logging
        """
        self._exchange_name = exchange_name
        self._logger = logging.getLogger(f"{__name__}.{exchange_name}")
        self._handlers: Dict[EventType, Set[Callable[[Event], None]]] = defaultdict(set)
        self._handler_interfaces: Set[ExchangeEventHandlerInterface] = set()
        self._lock = threading.Lock()
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Subscribe to an event type."""
        with self._lock:
            self._handlers[event_type].add(handler)
            self._logger.debug(f"Subscribed handler to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Unsubscribe from an event type."""
        with self._lock:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                self._logger.debug(f"Unsubscribed handler from {event_type.value}")
    
    def subscribe_all(self, handler: ExchangeEventHandlerInterface) -> None:
        """Subscribe to all events with a handler interface."""
        with self._lock:
            self._handler_interfaces.add(handler)
            self._logger.debug(f"Subscribed interface handler to all events")
    
    def unsubscribe_all(self, handler: ExchangeEventHandlerInterface) -> None:
        """Unsubscribe handler from all events."""
        with self._lock:
            if handler in self._handler_interfaces:
                self._handler_interfaces.remove(handler)
                self._logger.debug(f"Unsubscribed interface handler from all events")
    
    def emit(self, event: Event) -> None:
        """Emit an event to all subscribers."""
        # Make a copy to avoid issues if handlers modify subscriptions
        with self._lock:
            specific_handlers = list(self._handlers.get(event.event_type, []))
            interface_handlers = list(self._handler_interfaces)
        
        # Call specific handlers
        for handler in specific_handlers:
            try:
                handler(event)
            except Exception as e:
                self._logger.error(
                    f"Error in event handler for {event.event_type.value}: {e}",
                    exc_info=True
                )
        
        # Call interface handlers
        for handler in interface_handlers:
            try:
                # Call generic handler
                handler.on_event(event)
                
                # Call specific handler based on event type
                if isinstance(event, TickEvent):
                    handler.on_tick(event)
                elif isinstance(event, OrderEvent):
                    handler.on_order(event)
                elif isinstance(event, PositionEvent):
                    handler.on_position(event)
                elif event.event_type == EventType.ERROR:
                    handler.on_error(event)
                    
            except Exception as e:
                self._logger.error(
                    f"Error in interface handler for {event.event_type.value}: {e}",
                    exc_info=True
                )
    
    def clear_all_handlers(self) -> None:
        """Clear all event handlers (useful for cleanup)."""
        with self._lock:
            self._handlers.clear()
            self._handler_interfaces.clear()
            self._logger.debug("Cleared all event handlers")