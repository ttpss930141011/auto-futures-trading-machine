#!/usr/bin/env python3
"""Test script to verify DLL decoupling functionality."""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.infrastructure.exchange_adapters import ExchangeFactory, ExchangeProvider
from src.domain.interfaces.exchange_api_interface import (
    LoginCredentials,
    OrderRequest
)
from src.domain.interfaces.exchange_event_interface import (
    EventType,
    ExchangeEventHandlerInterface,
    Event,
    TickEvent,
    OrderEvent
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestEventHandler(ExchangeEventHandlerInterface):
    """Test event handler to verify event system."""
    
    def __init__(self):
        self.events_received = []
    
    def on_event(self, event: Event) -> None:
        """Log all events."""
        logger.info(f"Event received: {event.event_type.value}")
        self.events_received.append(event)
    
    def on_tick(self, tick: TickEvent) -> None:
        """Handle tick data."""
        logger.info(f"Tick: {tick.symbol} @ {tick.price} (bid: {tick.bid}, ask: {tick.ask})")
    
    def on_order(self, order: OrderEvent) -> None:
        """Handle order updates."""
        logger.info(f"Order: {order.order_id} - {order.status} for {order.symbol}")
    
    def on_position(self, position) -> None:
        """Handle position updates."""
        logger.info(f"Position: {position.symbol} - {position.quantity} @ {position.average_price}")
    
    def on_error(self, error: Event) -> None:
        """Handle errors."""
        logger.error(f"Error: {error.error}")


def test_simulator():
    """Test the simulator exchange implementation."""
    logger.info("=" * 60)
    logger.info("Testing Simulator Exchange")
    logger.info("=" * 60)
    
    # Create simulator
    os.environ['EXCHANGE_PROVIDER'] = 'SIMULATOR'
    exchange = ExchangeFactory.create_exchange_api()
    
    logger.info(f"Created exchange: {exchange.get_exchange_name()}")
    
    # Test event system
    event_handler = TestEventHandler()
    event_manager = exchange.get_event_manager()
    event_manager.subscribe_all(event_handler)
    
    # Test connection
    credentials = LoginCredentials(
        username="test",
        password="test",
        server_url="simulator://test",
        environment="test"
    )
    
    result = exchange.connect(credentials)
    logger.info(f"Connection result: {result}")
    assert result.success, "Connection should succeed with test credentials"
    
    # Verify login event was received
    assert len(event_handler.events_received) > 0, "Should receive login event"
    assert event_handler.events_received[0].event_type == EventType.LOGIN_SUCCESS
    
    # Test order sending
    order = OrderRequest(
        account="TEST001",
        symbol="TXFD4",
        side="BUY",
        order_type="MARKET",
        quantity=1,
        price=0.0,
        time_in_force="IOC",
        note="Test order"
    )
    
    order_result = exchange.send_order(order)
    logger.info(f"Order result: {order_result}")
    assert order_result.success, "Order should succeed"
    
    # Check order events
    order_events = [e for e in event_handler.events_received if isinstance(e, OrderEvent)]
    assert len(order_events) >= 1, "Should receive order events"
    
    # Test positions
    positions = exchange.get_positions("TEST001")
    logger.info(f"Positions: {positions}")
    
    # Test disconnection
    assert exchange.disconnect(), "Disconnection should succeed"
    
    logger.info("✅ Simulator test passed!")
    return True


def test_exchange_factory():
    """Test the exchange factory."""
    logger.info("=" * 60)
    logger.info("Testing Exchange Factory")
    logger.info("=" * 60)
    
    # Test supported providers
    providers = ExchangeFactory.get_supported_providers()
    logger.info(f"Supported providers: {providers}")
    assert "PFCF" in providers
    assert "SIMULATOR" in providers
    
    # Test provider validation
    assert ExchangeFactory.is_provider_supported("PFCF")
    assert ExchangeFactory.is_provider_supported("SIMULATOR")
    assert not ExchangeFactory.is_provider_supported("INVALID")
    
    logger.info("✅ Exchange factory test passed!")
    return True


def test_event_system():
    """Test the event system in isolation."""
    logger.info("=" * 60)
    logger.info("Testing Event System")
    logger.info("=" * 60)
    
    from src.infrastructure.events.exchange_event_manager import ExchangeEventManager
    
    # Create event manager
    manager = ExchangeEventManager("Test")
    
    # Test specific event subscription
    tick_count = 0
    def on_tick(event):
        nonlocal tick_count
        tick_count += 1
        logger.info(f"Received tick event: {event.event_type.value}")
    
    manager.subscribe(EventType.TICK_DATA, on_tick)
    
    # Emit tick event
    tick = TickEvent(
        event_type=EventType.TICK_DATA,
        timestamp="2024-01-01T12:00:00",
        data={},
        source="Test",
        symbol="TEST",
        price=100.0,
        volume=10,
        bid=99.5,
        ask=100.5,
        bid_volume=5,
        ask_volume=5
    )
    
    manager.emit(tick)
    assert tick_count == 1, "Should receive tick event"
    
    # Test handler interface
    handler = TestEventHandler()
    manager.subscribe_all(handler)
    
    # Emit various events
    manager.emit(tick)
    manager.emit(Event(
        event_type=EventType.ERROR,
        timestamp="2024-01-01T12:00:01",
        data={},
        source="Test",
        error="Test error"
    ))
    
    assert len(handler.events_received) >= 2, "Handler should receive events"
    
    logger.info("✅ Event system test passed!")
    return True


def main():
    """Run all tests."""
    try:
        logger.info("Starting DLL Decoupling Tests")
        
        # Run tests
        tests = [
            test_exchange_factory,
            test_event_system,
            test_simulator,
        ]
        
        for test in tests:
            if not test():
                logger.error(f"Test {test.__name__} failed!")
                return 1
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ All tests passed successfully!")
        logger.info("=" * 60)
        return 0
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())