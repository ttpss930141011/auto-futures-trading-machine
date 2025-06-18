"""Exchange Switching Integration Test - Test switching between different exchanges."""

import pytest
import logging
from typing import List

from src.infrastructure.exchange_adapters import ExchangeFactory, ExchangeProvider
from src.infrastructure.services.service_container import ServiceContainer
from src.domain.interfaces.exchange_api_interface import (
    LoginCredentials,
    OrderRequest
)
from src.interactor.use_cases.v2.send_order_v2 import SendOrderV2UseCase
from src.interactor.use_cases.v2.get_positions_v2 import GetPositionsV2UseCase
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto
from src.interactor.dtos.get_position_dtos import GetPositionInputDto
from src.domain.value_objects import OrderOperation, OrderTypeEnum, TimeInForce, OpenClose, DayTrade


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestExchangeSwitching:
    """Test seamless switching between different exchange implementations."""
    
    @pytest.fixture
    def service_container(self):
        """Create a mock service container."""
        # Create a minimal service container for testing
        container = ServiceContainer()
        return container
    
    @pytest.fixture
    def exchange_factory(self, service_container):
        """Create exchange factory."""
        return ExchangeFactory(service_container)
    
    def test_switch_between_exchanges(self, exchange_factory):
        """Test switching between simulator and PFCF exchanges."""
        logger.info("=== Testing Exchange Switching ===")
        
        # Test credentials
        test_credentials = LoginCredentials(
            username="test",
            password="test",
            server_url="http://test.com",
            environment="test"
        )
        
        # List of exchanges to test
        exchanges_to_test = [
            ExchangeProvider.SIMULATOR,
            # ExchangeProvider.PFCF,  # Skip PFCF for now as it requires real DLL
        ]
        
        # Test each exchange
        for provider in exchanges_to_test:
            logger.info(f"\n--- Testing {provider.value} Exchange ---")
            
            # Create exchange instance
            exchange = exchange_factory.create_exchange(provider)
            assert exchange is not None
            
            # Connect to exchange
            login_result = exchange.connect(test_credentials)
            assert login_result.success
            logger.info(f"✅ Connected to {exchange.get_exchange_name()}")
            
            # Create V2 use cases with this exchange
            send_order_use_case = SendOrderV2UseCase(exchange)
            get_positions_use_case = GetPositionsV2UseCase(exchange)
            
            # Test sending order
            order_dto = SendMarketOrderInputDto(
                order_account="TEST001",
                item_code="TXFD4",
                side=OrderOperation.BUY,
                order_type=OrderTypeEnum.Market,
                quantity=1,
                price=0.0,
                time_in_force=TimeInForce.IOC,
                open_close=OpenClose.AUTO,
                day_trade=DayTrade.No,
                note="Test order"
            )
            
            order_result = send_order_use_case.execute(order_dto)
            assert order_result.is_send_order
            logger.info(f"✅ Order sent: {order_result.order_serial}")
            
            # Test getting positions
            position_dto = GetPositionInputDto(account_id="TEST001")
            position_result = get_positions_use_case.execute(position_dto)
            assert position_result.success
            logger.info(f"✅ Retrieved {len(position_result.positions)} positions")
            
            # Disconnect
            assert exchange.disconnect()
            logger.info(f"✅ Disconnected from {exchange.get_exchange_name()}")
    
    def test_concurrent_multiple_exchanges(self, exchange_factory):
        """Test using multiple exchanges concurrently."""
        logger.info("\n=== Testing Concurrent Multiple Exchanges ===")
        
        # Create multiple exchange instances
        sim1 = exchange_factory.create_exchange(ExchangeProvider.SIMULATOR)
        sim2 = exchange_factory.create_exchange(ExchangeProvider.SIMULATOR)
        
        # Connect both
        creds = LoginCredentials("user1", "pass1", "http://sim1.com", "test")
        assert sim1.connect(creds).success
        
        creds2 = LoginCredentials("user2", "pass2", "http://sim2.com", "test")
        assert sim2.connect(creds2).success
        
        logger.info("✅ Connected to multiple exchanges concurrently")
        
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
        assert result1.order_id != result2.order_id  # Different order IDs
        
        logger.info(f"✅ Sent orders to both exchanges: {result1.order_id}, {result2.order_id}")
        
        # Cleanup
        sim1.disconnect()
        sim2.disconnect()
    
    def test_exchange_specific_features(self, exchange_factory):
        """Test that exchange-specific features are preserved."""
        logger.info("\n=== Testing Exchange-Specific Features ===")
        
        # Create simulator exchange
        exchange = exchange_factory.create_exchange(ExchangeProvider.SIMULATOR)
        
        # Test that event manager is available
        event_manager = exchange.get_event_manager()
        assert event_manager is not None
        
        # Subscribe to events
        events_received = []
        
        def on_event(event_type: str, data: dict):
            events_received.append((event_type, data))
        
        event_manager.subscribe("order_filled", on_event)
        
        # Connect and send order
        creds = LoginCredentials("test", "test", "http://test.com", "test")
        exchange.connect(creds)
        
        order = OrderRequest(
            account="TEST",
            symbol="TXFD4",
            side="BUY",
            order_type="MARKET",
            quantity=1,
            price=0.0,
            time_in_force="IOC"
        )
        
        result = exchange.send_order(order)
        assert result.success
        
        # Check events were received
        assert len(events_received) > 0
        logger.info(f"✅ Received {len(events_received)} events")
        
        exchange.disconnect()


if __name__ == "__main__":
    # Run tests directly
    test = TestExchangeSwitching()
    
    # Create mock service container
    container = ServiceContainer()
    factory = ExchangeFactory(container)
    
    try:
        test.test_switch_between_exchanges(factory)
        test.test_concurrent_multiple_exchanges(factory)
        test.test_exchange_specific_features(factory)
        
        logger.info("\n✅ All exchange switching tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise