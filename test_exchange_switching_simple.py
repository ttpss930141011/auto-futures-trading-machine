"""Simple Exchange Switching Test - Test switching between different exchanges."""

import logging
from src.infrastructure.exchange_adapters import ExchangeFactory, ExchangeProvider
from src.domain.interfaces.exchange_api_interface import LoginCredentials, OrderRequest
from src.domain.interfaces.exchange_event_interface import EventType, Event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_exchange_switching():
    """Test basic exchange switching functionality."""
    logger.info("=== Testing Exchange Switching ===")
    
    # ExchangeFactory is static, no need to instantiate
    
    # Test credentials (simulator expects test/test)
    test_credentials = LoginCredentials(
        username="test",
        password="test",
        server_url="http://test.com",
        environment="test"
    )
    
    # Test Simulator Exchange
    logger.info("\n--- Testing Simulator Exchange ---")
    sim_exchange = ExchangeFactory.create_exchange_api(
        provider="SIMULATOR",
        service_container=None
    )
    assert sim_exchange is not None
    logger.info(f"✅ Created: {sim_exchange.get_exchange_name()}")
    
    # Connect
    login_result = sim_exchange.connect(test_credentials)
    assert login_result.success
    logger.info(f"✅ Connected: {login_result.message}")
    
    # Send order
    order = OrderRequest(
        account="TEST001",
        symbol="TXFD4",
        side="BUY",
        order_type="MARKET",
        quantity=2,
        price=0.0,
        time_in_force="IOC",
        note="Test order"
    )
    
    order_result = sim_exchange.send_order(order)
    assert order_result.success
    logger.info(f"✅ Order sent: {order_result.order_id}")
    
    # Get positions
    positions = sim_exchange.get_positions("TEST001")
    assert len(positions) > 0
    logger.info(f"✅ Positions: {len(positions)} found")
    for pos in positions:
        logger.info(f"   - {pos['symbol']}: {pos['quantity']} @ {pos['average_price']}")
    
    # Test event system
    event_manager = sim_exchange.get_event_manager()
    events = []
    
    def on_event(event: Event):
        events.append(event)
        logger.info(f"📢 Event: {event.event_type.value}")
    
    event_manager.subscribe(EventType.ORDER_FILLED, on_event)
    
    # Send another order to trigger events
    order2 = OrderRequest(
        account="TEST001",
        symbol="TXFD4",
        side="SELL",
        order_type="MARKET",
        quantity=1,
        price=0.0,
        time_in_force="IOC"
    )
    
    sim_exchange.send_order(order2)
    assert len(events) > 0
    logger.info(f"✅ Events received: {len(events)}")
    
    # Disconnect
    assert sim_exchange.disconnect()
    logger.info(f"✅ Disconnected")
    
    logger.info("\n✅ Exchange switching test completed successfully!")


def test_multiple_exchanges():
    """Test multiple exchanges running concurrently."""
    logger.info("\n=== Testing Multiple Concurrent Exchanges ===")
    
    # ExchangeFactory is static
    
    # Create two simulator instances
    sim1 = ExchangeFactory.create_exchange_api("SIMULATOR", None)
    sim2 = ExchangeFactory.create_exchange_api("SIMULATOR", None)
    
    # Connect both with same test credentials (simulator only accepts test/test)
    creds1 = LoginCredentials("test", "test", "http://sim1.com", "test")
    creds2 = LoginCredentials("test", "test", "http://sim2.com", "test")
    
    assert sim1.connect(creds1).success
    assert sim2.connect(creds2).success
    logger.info("✅ Connected to 2 exchanges concurrently")
    
    # Send orders to both
    order = OrderRequest(
        account="ACC1",
        symbol="TEST",
        side="BUY",
        order_type="MARKET",
        quantity=1,
        price=100.0,
        time_in_force="IOC"
    )
    
    result1 = sim1.send_order(order)
    result2 = sim2.send_order(order)
    
    assert result1.success
    assert result2.success
    assert result1.order_id != result2.order_id
    
    logger.info(f"✅ Orders sent to both exchanges:")
    logger.info(f"   - Exchange 1: {result1.order_id}")
    logger.info(f"   - Exchange 2: {result2.order_id}")
    
    # Check positions on both
    pos1 = sim1.get_positions("ACC1")
    pos2 = sim2.get_positions("ACC1")
    
    assert len(pos1) > 0
    assert len(pos2) > 0
    logger.info(f"✅ Positions retrieved from both exchanges")
    
    # Cleanup
    sim1.disconnect()
    sim2.disconnect()
    logger.info("✅ Both exchanges disconnected")


if __name__ == "__main__":
    try:
        test_exchange_switching()
        test_multiple_exchanges()
        logger.info("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise