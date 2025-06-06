"""Tests for OrderExecutorGateway.

This module contains comprehensive tests for the OrderExecutorGateway,
including signal processing, gateway integration, and error handling.
"""

import pytest
from unittest.mock import Mock, MagicMock, call
from datetime import datetime

from src.domain.order.order_executor_gateway import OrderExecutorGateway
from src.infrastructure.messaging import ZmqPuller
from src.infrastructure.events.trading_signal import TradingSignal
from src.domain.value_objects import OrderOperation
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.dll_gateway_service_interface import (
    DllGatewayServiceInterface,
    OrderRequest,
    OrderResponse,
)
from src.interactor.errors.dll_gateway_errors import DllGatewayError


class TestOrderExecutorGateway:
    """Test suite for OrderExecutorGateway.
    
    Tests signal processing, order execution via gateway,
    error handling, and integration scenarios.
    """

    @pytest.fixture
    def mock_signal_puller(self):
        """Create mock signal puller."""
        return Mock(spec=ZmqPuller)

    @pytest.fixture
    def mock_dll_gateway_service(self):
        """Create mock DLL gateway service."""
        return Mock(spec=DllGatewayServiceInterface)

    @pytest.fixture
    def mock_session_repository(self):
        """Create mock session repository."""
        return Mock(spec=SessionRepositoryInterface)

    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock(spec=LoggerInterface)

    @pytest.fixture
    def order_executor(self, mock_signal_puller, mock_dll_gateway_service, 
                      mock_session_repository, mock_logger):
        """Create OrderExecutorGateway instance for testing."""
        return OrderExecutorGateway(
            signal_puller=mock_signal_puller,
            dll_gateway_service=mock_dll_gateway_service,
            session_repository=mock_session_repository,
            logger=mock_logger,
            default_quantity=2
        )

    @pytest.fixture
    def sample_trading_signal(self):
        """Create sample trading signal for testing."""
        return TradingSignal(
            commodity_id="TXFF4",
            operation=OrderOperation.Buy,
            when=datetime.now()
        )

    def test_initialization(self, order_executor, mock_signal_puller, 
                           mock_dll_gateway_service, mock_session_repository, mock_logger):
        """Test proper initialization of OrderExecutorGateway."""
        assert order_executor._signal_puller == mock_signal_puller
        assert order_executor._dll_gateway_service == mock_dll_gateway_service
        assert order_executor._session_repository == mock_session_repository
        assert order_executor._logger == mock_logger
        assert order_executor._default_quantity == 2

    def test_process_received_signal_no_signal(self, order_executor, mock_signal_puller):
        """Test processing when no signal is received."""
        mock_signal_puller.receive.return_value = None
        
        result = order_executor.process_received_signal()
        
        assert result is False
        mock_signal_puller.receive.assert_called_once_with(non_blocking=True)

    def test_process_received_signal_success(self, order_executor, mock_signal_puller,
                                           mock_session_repository, mock_dll_gateway_service,
                                           mock_logger, sample_trading_signal):
        """Test successful signal processing and order execution."""
        # Setup mocks
        serialized_signal = b"serialized_signal"
        mock_signal_puller.receive.return_value = serialized_signal
        mock_session_repository.get_order_account.return_value = "TEST001"
        mock_dll_gateway_service.is_connected.return_value = True
        mock_dll_gateway_service.send_order.return_value = OrderResponse(
            success=True, order_id="ORDER123"
        )
        
        # Mock deserialize function
        with pytest.mock.patch('src.domain.order.order_executor_gateway.deserialize') as mock_deserialize:
            mock_deserialize.return_value = sample_trading_signal
            
            result = order_executor.process_received_signal()
        
        # Verify result
        assert result is True
        
        # Verify interactions
        mock_signal_puller.receive.assert_called_once_with(non_blocking=True)
        mock_deserialize.assert_called_once_with(serialized_signal)
        mock_session_repository.get_order_account.assert_called_once()
        mock_dll_gateway_service.is_connected.assert_called_once()
        mock_dll_gateway_service.send_order.assert_called_once()
        
        # Verify logging
        mock_logger.log_info.assert_any_call(
            f"Received trading signal via ZMQ: {sample_trading_signal.operation.name} "
            f"{sample_trading_signal.commodity_id} at {sample_trading_signal.when}"
        )

    def test_process_received_signal_invalid_type(self, order_executor, mock_signal_puller,
                                                 mock_logger):
        """Test processing when received message is not a TradingSignal."""
        # Setup mocks
        serialized_signal = b"serialized_signal"
        mock_signal_puller.receive.return_value = serialized_signal
        
        # Mock deserialize to return wrong type
        with pytest.mock.patch('src.domain.order.order_executor_gateway.deserialize') as mock_deserialize:
            mock_deserialize.return_value = "not_a_trading_signal"
            
            result = order_executor.process_received_signal()
        
        # Verify result
        assert result is True  # Message consumed even if wrong type
        
        # Verify warning logged
        mock_logger.log_warning.assert_called_once_with(
            "Received non-TradingSignal message: <class 'str'>"
        )

    def test_process_received_signal_deserialization_error(self, order_executor, mock_signal_puller,
                                                          mock_logger):
        """Test handling of deserialization errors."""
        # Setup mocks
        serialized_signal = b"invalid_signal"
        mock_signal_puller.receive.return_value = serialized_signal
        
        # Mock deserialize to raise exception
        with pytest.mock.patch('src.domain.order.order_executor_gateway.deserialize') as mock_deserialize:
            mock_deserialize.side_effect = Exception("Deserialization error")
            
            result = order_executor.process_received_signal()
        
        # Verify result
        assert result is True  # Message consumed even if error
        
        # Verify error logged
        mock_logger.log_error.assert_called_once()
        error_message = mock_logger.log_error.call_args[0][0]
        assert "Failed to deserialize or process received ZMQ message" in error_message

    def test_process_trading_signal_no_order_account(self, order_executor, mock_session_repository,
                                                    mock_logger, sample_trading_signal):
        """Test processing signal when no order account is available."""
        mock_session_repository.get_order_account.return_value = None
        
        order_executor._process_trading_signal(sample_trading_signal)
        
        mock_logger.log_error.assert_called_once_with(
            "Cannot execute order: No order account selected"
        )

    def test_create_order_request(self, order_executor, sample_trading_signal):
        """Test creation of order request from trading signal."""
        order_account = "TEST001"
        
        order_request = order_executor._create_order_request(sample_trading_signal, order_account)
        
        assert isinstance(order_request, OrderRequest)
        assert order_request.order_account == order_account
        assert order_request.item_code == sample_trading_signal.commodity_id
        assert order_request.side == sample_trading_signal.operation.name
        assert order_request.quantity == 2  # default_quantity
        assert order_request.note == "From AFTM Gateway"

    def test_execute_order_via_gateway_success(self, order_executor, mock_dll_gateway_service,
                                              mock_logger):
        """Test successful order execution via gateway."""
        # Setup mocks
        mock_dll_gateway_service.is_connected.return_value = True
        mock_dll_gateway_service.send_order.return_value = OrderResponse(
            success=True, order_id="ORDER456"
        )
        
        # Create order request
        order_request = OrderRequest(
            order_account="TEST001",
            item_code="TXFF4",
            side="Buy",
            order_type="Market",
            price=0.0,
            quantity=1,
            open_close="AUTO",
            note="Test",
            day_trade="No",
            time_in_force="IOC"
        )
        
        order_executor._execute_order_via_gateway(order_request)
        
        # Verify gateway calls
        mock_dll_gateway_service.is_connected.assert_called_once()
        mock_dll_gateway_service.send_order.assert_called_once_with(order_request)
        
        # Verify success logging
        mock_logger.log_info.assert_any_call(
            "Order executed successfully via DLL Gateway. Order ID: ORDER456"
        )

    def test_execute_order_via_gateway_not_connected(self, order_executor, mock_dll_gateway_service,
                                                    mock_logger):
        """Test order execution when gateway is not connected."""
        mock_dll_gateway_service.is_connected.return_value = False
        
        order_request = OrderRequest(
            order_account="TEST001",
            item_code="TXFF4",
            side="Buy",
            order_type="Market",
            price=0.0,
            quantity=1,
            open_close="AUTO",
            note="Test",
            day_trade="No",
            time_in_force="IOC"
        )
        
        order_executor._execute_order_via_gateway(order_request)
        
        # Verify error logged
        mock_logger.log_error.assert_called_with("DLL Gateway is not connected")
        
        # Verify send_order was not called
        mock_dll_gateway_service.send_order.assert_not_called()

    def test_execute_order_via_gateway_failure(self, order_executor, mock_dll_gateway_service,
                                              mock_logger):
        """Test order execution failure via gateway."""
        # Setup mocks
        mock_dll_gateway_service.is_connected.return_value = True
        mock_dll_gateway_service.send_order.return_value = OrderResponse(
            success=False, 
            error_message="Invalid order parameters",
            error_code="INVALID_PARAMS"
        )
        
        order_request = OrderRequest(
            order_account="TEST001",
            item_code="TXFF4",
            side="Buy",
            order_type="Market",
            price=0.0,
            quantity=1,
            open_close="AUTO",
            note="Test",
            day_trade="No",
            time_in_force="IOC"
        )
        
        order_executor._execute_order_via_gateway(order_request)
        
        # Verify error logging
        mock_logger.log_error.assert_called_with(
            "Order execution failed via DLL Gateway. "
            "Error: Invalid order parameters (Code: INVALID_PARAMS)"
        )

    def test_execute_order_via_gateway_exception(self, order_executor, mock_dll_gateway_service,
                                                mock_logger):
        """Test handling of gateway exceptions during order execution."""
        # Setup mocks
        mock_dll_gateway_service.is_connected.return_value = True
        mock_dll_gateway_service.send_order.side_effect = DllGatewayError("Gateway error")
        
        order_request = OrderRequest(
            order_account="TEST001",
            item_code="TXFF4",
            side="Buy",
            order_type="Market",
            price=0.0,
            quantity=1,
            open_close="AUTO",
            note="Test",
            day_trade="No",
            time_in_force="IOC"
        )
        
        order_executor._execute_order_via_gateway(order_request)
        
        # Verify error logging
        mock_logger.log_error.assert_called_with(
            "DLL Gateway error during order execution: Gateway error"
        )

    def test_get_health_status_success(self, order_executor, mock_dll_gateway_service):
        """Test successful health status retrieval."""
        gateway_health = {
            "status": "healthy",
            "exchange_connected": True,
            "timestamp": 1234567890
        }
        mock_dll_gateway_service.get_health_status.return_value = gateway_health
        
        health_status = order_executor.get_health_status()
        
        assert health_status["order_executor_running"] is True
        assert health_status["gateway_status"] == gateway_health
        assert health_status["signal_puller_active"] is True

    def test_get_health_status_error(self, order_executor, mock_dll_gateway_service, mock_logger):
        """Test health status retrieval when gateway raises exception."""
        mock_dll_gateway_service.get_health_status.side_effect = Exception("Gateway down")
        
        health_status = order_executor.get_health_status()
        
        assert health_status["order_executor_running"] is True
        assert health_status["gateway_status"]["status"] == "unhealthy"
        assert "Gateway down" in health_status["gateway_status"]["error"]
        
        # Verify error logged
        mock_logger.log_error.assert_called_once()

    def test_close(self, order_executor, mock_dll_gateway_service, mock_logger):
        """Test resource cleanup during close."""
        # Add close method to mock
        mock_dll_gateway_service.close = Mock()
        
        order_executor.close()
        
        # Verify cleanup logged
        mock_logger.log_info.assert_called_with("Closing OrderExecutorGateway resources")
        
        # Verify gateway close called
        mock_dll_gateway_service.close.assert_called_once()

    def test_context_manager(self, order_executor):
        """Test OrderExecutorGateway as context manager."""
        with order_executor as executor:
            assert executor is order_executor
        # close() should be called automatically

    def test_integration_signal_to_order_flow(self, order_executor, mock_signal_puller,
                                             mock_session_repository, mock_dll_gateway_service,
                                             mock_logger, sample_trading_signal):
        """Test complete integration flow from signal to order execution."""
        # Setup full mock chain
        serialized_signal = b"serialized_trading_signal"
        mock_signal_puller.receive.return_value = serialized_signal
        mock_session_repository.get_order_account.return_value = "INTEGRATION_TEST"
        mock_dll_gateway_service.is_connected.return_value = True
        mock_dll_gateway_service.send_order.return_value = OrderResponse(
            success=True, order_id="INTEGRATION_ORDER_789"
        )
        
        # Mock deserialize
        with pytest.mock.patch('src.domain.order.order_executor_gateway.deserialize') as mock_deserialize:
            mock_deserialize.return_value = sample_trading_signal
            
            # Execute the flow
            result = order_executor.process_received_signal()
        
        # Verify complete flow
        assert result is True
        
        # Verify all components were called
        mock_signal_puller.receive.assert_called_once()
        mock_session_repository.get_order_account.assert_called_once()
        mock_dll_gateway_service.is_connected.assert_called_once()
        mock_dll_gateway_service.send_order.assert_called_once()
        
        # Verify order request was properly constructed
        sent_order = mock_dll_gateway_service.send_order.call_args[0][0]
        assert sent_order.order_account == "INTEGRATION_TEST"
        assert sent_order.item_code == sample_trading_signal.commodity_id
        assert sent_order.side == sample_trading_signal.operation.name
        assert sent_order.quantity == 2  # default_quantity
        
        # Verify logging of success
        success_calls = [call for call in mock_logger.log_info.call_args_list 
                        if "Order executed successfully" in str(call)]
        assert len(success_calls) == 1