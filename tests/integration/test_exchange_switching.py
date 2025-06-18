"""Exchange Switching Integration Test - Test switching between different exchanges."""

import pytest
import logging
from typing import List

from src.infrastructure.exchange_adapters import ExchangeFactory, ExchangeProvider
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
        # ServiceContainer is not needed for these tests
        return None
    
    # No need for exchange_factory fixture - ExchangeFactory is static
    
    def test_switch_between_exchanges(self):
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
            exchange = ExchangeFactory.create_exchange_api(
                provider=provider.value,
                service_container=None
            )
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
            position_dto = GetPositionInputDto(order_account="TEST001")
            position_result = get_positions_use_case.execute(position_dto)
            assert not position_result.has_error
            logger.info(f"✅ Retrieved {position_result.total_positions} positions")
            
            # Disconnect
            assert exchange.disconnect()
            logger.info(f"✅ Disconnected from {exchange.get_exchange_name()}")
    
    def test_concurrent_multiple_exchanges(self):
        """Test using multiple exchanges concurrently."""
        logger.info("\n=== Testing Concurrent Multiple Exchanges ===")
        
        # Create multiple exchange instances
        sim1 = ExchangeFactory.create_exchange_api("SIMULATOR", None)
        sim2 = ExchangeFactory.create_exchange_api("SIMULATOR", None)
        
        # Connect both with test credentials (simulator only accepts test/test)
        creds = LoginCredentials("test", "test", "http://sim1.com", "test")
        assert sim1.connect(creds).success
        
        creds2 = LoginCredentials("test", "test", "http://sim2.com", "test")
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
    
    def test_exchange_specific_features(self):
        """Test that exchange-specific features are preserved."""
        logger.info("\n=== Testing Exchange-Specific Features ===")
        
        # Create simulator exchange
        exchange = ExchangeFactory.create_exchange_api("SIMULATOR", None)
        
        # Test that event manager is available
        event_manager = exchange.get_event_manager()
        assert event_manager is not None
        
        # Subscribe to events
        events_received = []
        
        from src.domain.interfaces.exchange_event_interface import EventType, Event
        
        def on_event(event: Event):
            events_received.append(event)
        
        event_manager.subscribe(EventType.ORDER_FILLED, on_event)
        
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
