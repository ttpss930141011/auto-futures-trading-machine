"""Tests for Market Data Gateway Service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import zmq

from src.infrastructure.services.gateway.market_data_gateway_service import MarketDataGatewayService


class TestMarketDataGatewayService:
    """Test cases for MarketDataGatewayService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.ZMQ_TICK_PUB_ADDRESS = "tcp://127.0.0.1:5555"
        self.mock_config.ZMQ_SIGNAL_PUB_ADDRESS = "tcp://127.0.0.1:5556"
        
        self.mock_logger = Mock()
        self.mock_exchange_api = Mock()

    def test_initialization(self):
        """Test service initialization."""
        service = MarketDataGatewayService(
            self.mock_config, 
            self.mock_logger, 
            self.mock_exchange_api
        )
        
        assert service.config == self.mock_config
        assert service.logger == self.mock_logger
        assert service.exchange_api == self.mock_exchange_api
        assert not service._is_initialized
        assert service._tick_publisher is None
        assert service._tick_producer is None

    @patch('zmq.Context.instance')
    def test_zmq_context_creation(self, mock_context_instance):
        """Test ZMQ context creation."""
        mock_context = Mock()
        mock_context_instance.return_value = mock_context
        
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        assert service.zmq_context == mock_context
        mock_context_instance.assert_called_once()

    @patch('src.infrastructure.services.gateway.market_data_gateway_service.TickProducer')
    @patch('src.infrastructure.services.gateway.market_data_gateway_service.ZmqPublisher')
    def test_initialize_market_data_publisher_success(self, mock_zmq_publisher, mock_tick_producer):
        """Test successful market data publisher initialization."""
        # Mock publisher and producer instances
        mock_publisher_instance = Mock()
        mock_producer_instance = Mock()
        mock_zmq_publisher.return_value = mock_publisher_instance
        mock_tick_producer.return_value = mock_producer_instance
        
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Test initialization
        result = service.initialize_market_data_publisher()
        
        assert result is True
        assert service._is_initialized is True
        assert service._tick_publisher == mock_publisher_instance
        assert service._tick_producer == mock_producer_instance
        
        # Verify logger was called
        self.mock_logger.log_info.assert_called()

    @patch('src.infrastructure.services.gateway.market_data_gateway_service.TickProducer')
    @patch('src.infrastructure.services.gateway.market_data_gateway_service.ZmqPublisher')
    def test_initialize_market_data_publisher_failure(self, mock_zmq_publisher, mock_tick_producer):
        """Test market data publisher initialization failure."""
        # Mock ZmqPublisher to raise exception
        mock_zmq_publisher.side_effect = Exception("ZMQ initialization failed")
        
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Test initialization failure
        result = service.initialize_market_data_publisher()
        
        assert result is False
        assert service._is_initialized is False
        
        # Verify error was logged
        self.mock_logger.log_error.assert_called()

    def test_is_running_when_not_initialized(self):
        """Test is_running when service is not initialized."""
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        result = service.is_running()
        
        assert result is False

    @patch('src.infrastructure.services.gateway.market_data_gateway_service.TickProducer')
    @patch('src.infrastructure.services.gateway.market_data_gateway_service.ZmqPublisher')
    def test_is_running_when_initialized(self, mock_zmq_publisher, mock_tick_producer):
        """Test is_running when service is initialized."""
        # Setup mocks
        mock_publisher_instance = Mock()
        mock_producer_instance = Mock()
        mock_zmq_publisher.return_value = mock_publisher_instance
        mock_tick_producer.return_value = mock_producer_instance
        
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Initialize service
        service.initialize_market_data_publisher()
        
        result = service.is_running()
        
        assert result is True

    @patch('src.infrastructure.services.gateway.market_data_gateway_service.TickProducer')
    @patch('src.infrastructure.services.gateway.market_data_gateway_service.ZmqPublisher')
    def test_start_service_not_initialized(self, mock_zmq_publisher, mock_tick_producer):
        """Test starting service when not initialized."""
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        result = service.start()
        
        assert result is False
        self.mock_logger.log_warning.assert_called()

    @patch('src.infrastructure.services.gateway.market_data_gateway_service.TickProducer')
    @patch('src.infrastructure.services.gateway.market_data_gateway_service.ZmqPublisher')
    def test_start_service_success(self, mock_zmq_publisher, mock_tick_producer):
        """Test successful service start."""
        # Setup mocks
        mock_publisher_instance = Mock()
        mock_producer_instance = Mock()
        mock_producer_instance.start.return_value = True
        mock_zmq_publisher.return_value = mock_publisher_instance
        mock_tick_producer.return_value = mock_producer_instance
        
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Initialize and start service
        service.initialize_market_data_publisher()
        result = service.start()
        
        assert result is True
        mock_producer_instance.start.assert_called_once()
        self.mock_logger.log_info.assert_called()

    @patch('src.infrastructure.services.gateway.market_data_gateway_service.TickProducer')
    @patch('src.infrastructure.services.gateway.market_data_gateway_service.ZmqPublisher')
    def test_start_service_failure(self, mock_zmq_publisher, mock_tick_producer):
        """Test service start failure."""
        # Setup mocks
        mock_publisher_instance = Mock()
        mock_producer_instance = Mock()
        mock_producer_instance.start.return_value = False
        mock_zmq_publisher.return_value = mock_publisher_instance
        mock_tick_producer.return_value = mock_producer_instance
        
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Initialize and start service
        service.initialize_market_data_publisher()
        result = service.start()
        
        assert result is False
        self.mock_logger.log_error.assert_called()

    @patch('src.infrastructure.services.gateway.market_data_gateway_service.TickProducer')
    @patch('src.infrastructure.services.gateway.market_data_gateway_service.ZmqPublisher')
    def test_stop_service(self, mock_zmq_publisher, mock_tick_producer):
        """Test service stop."""
        # Setup mocks
        mock_publisher_instance = Mock()
        mock_producer_instance = Mock()
        mock_zmq_publisher.return_value = mock_publisher_instance
        mock_tick_producer.return_value = mock_producer_instance
        
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Initialize service
        service.initialize_market_data_publisher()
        
        # Stop service
        service.stop()
        
        # Verify components were stopped
        mock_producer_instance.stop.assert_called_once()
        mock_publisher_instance.close.assert_called_once()
        
        assert service._is_initialized is False
        self.mock_logger.log_info.assert_called()

    def test_stop_service_not_initialized(self):
        """Test stopping service when not initialized."""
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Should handle gracefully
        service.stop()
        
        # Should log appropriate message
        self.mock_logger.log_info.assert_called()

    @patch('src.infrastructure.services.gateway.market_data_gateway_service.TickProducer')
    @patch('src.infrastructure.services.gateway.market_data_gateway_service.ZmqPublisher')
    def test_stop_service_with_exceptions(self, mock_zmq_publisher, mock_tick_producer):
        """Test service stop with exceptions during cleanup."""
        # Setup mocks that raise exceptions
        mock_publisher_instance = Mock()
        mock_producer_instance = Mock()
        mock_producer_instance.stop.side_effect = Exception("Stop failed")
        mock_publisher_instance.close.side_effect = Exception("Close failed")
        mock_zmq_publisher.return_value = mock_publisher_instance
        mock_tick_producer.return_value = mock_producer_instance
        
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Initialize service
        service.initialize_market_data_publisher()
        
        # Stop service - should handle exceptions gracefully
        service.stop()
        
        # Should still mark as not initialized
        assert service._is_initialized is False
        self.mock_logger.log_error.assert_called()

    def test_properties_access(self):
        """Test access to service properties."""
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Should be able to access all properties
        assert service.config is not None
        assert service.logger is not None
        assert service.exchange_api is not None
        assert service.zmq_context is not None

    def test_service_state_consistency(self):
        """Test service state consistency throughout lifecycle."""
        service = MarketDataGatewayService(
            self.mock_config,
            self.mock_logger,
            self.mock_exchange_api
        )
        
        # Initial state
        assert not service.is_running()
        assert not service._is_initialized
        
        # After initialization
        with patch('src.infrastructure.services.gateway.market_data_gateway_service.ZmqPublisher'), \
             patch('src.infrastructure.services.gateway.market_data_gateway_service.TickProducer'):
            
            service.initialize_market_data_publisher()
            assert service.is_running()
            assert service._is_initialized
            
            # After stop
            service.stop()
            assert not service.is_running()
            assert not service._is_initialized