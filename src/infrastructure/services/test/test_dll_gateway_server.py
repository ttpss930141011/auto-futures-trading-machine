"""Tests for DLL Gateway Server.

This module contains comprehensive tests for the DLL Gateway Server,
including functionality, error handling, and integration scenarios.
"""

import json
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.services.dll_gateway_server import DllGatewayServer
from src.interactor.interfaces.logger.logger import LoggerInterface


class TestDllGatewayServer:
    """Test suite for DLL Gateway Server.

    Tests server functionality, request processing, error handling,
    and integration with ZeroMQ and exchange API.
    """

    @pytest.fixture
    def mock_exchange_client(self):
        """Create mock exchange client."""
        mock_client = Mock()

        # Mock the send_order method
        mock_client.send_order = Mock()

        # Keep legacy attributes for backward compatibility with old tests
        mock_client.client = Mock()
        mock_client.client.DTradeLib = Mock()
        mock_client.client.DAccountLib = Mock()
        mock_client.trade = Mock()
        mock_client.trade.OrderObject = Mock()
        mock_client.decimal = Mock()
        mock_client.decimal.Parse.return_value = 0.0

        return mock_client

    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock(spec=LoggerInterface)

    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        return Mock()

    @pytest.fixture
    def server_address(self):
        """Provide test server address."""
        return "tcp://127.0.0.1:15557"  # Use different port to avoid conflicts

    @pytest.fixture
    def gateway_server(self, mock_exchange_client, mock_config, mock_logger, server_address):
        """Create DLL Gateway Server instance for testing."""
        return DllGatewayServer(
            exchange_client=mock_exchange_client,
            config=mock_config,
            logger=mock_logger,
            bind_address=server_address,
            request_timeout_ms=1000,
        )

    def test_server_initialization(self, gateway_server, mock_exchange_client, mock_config, mock_logger):
        """Test server initialization with proper dependencies."""
        # pylint: disable=protected-access
        assert gateway_server._exchange_client == mock_exchange_client
        assert gateway_server._config == mock_config
        assert gateway_server._logger == mock_logger
        assert gateway_server._context is None
        assert gateway_server._socket is None
        assert gateway_server._running is False

    def test_server_start_success(self, gateway_server, mock_logger):
        """Test successful server startup."""
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_context.return_value.socket.return_value = mock_socket

            result = gateway_server.start()
            assert result is True
            # pylint: disable=protected-access
            assert gateway_server._running is True
            mock_logger.log_info.assert_called()

    def test_server_start_already_running(self, gateway_server, mock_logger):
        """Test starting server when already running."""
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_context.return_value.socket.return_value = mock_socket

            gateway_server.start()
            result = gateway_server.start()  # Try to start again
            assert result is True
            mock_logger.log_warning.assert_called_with("DLL Gateway Server is already running")

    def test_server_stop(self, gateway_server):
        """Test server graceful shutdown."""
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_context.return_value.socket.return_value = mock_socket

            gateway_server.start()
            # pylint: disable=protected-access
            assert gateway_server._running is True

            gateway_server.stop()
            # pylint: disable=protected-access
            assert gateway_server._running is False

    def test_context_manager(self, gateway_server):
        """Test server as context manager."""
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_context.return_value.socket.return_value = mock_socket

            with gateway_server as server:
                # pylint: disable=protected-access
                assert server._running is True
            # pylint: disable=protected-access
            assert gateway_server._running is False

    def test_send_order_request_processing(self, gateway_server, mock_exchange_client, mock_config):  # pylint: disable=unused-argument
        """Test processing of send order requests."""
        # Setup mock order result
        from src.domain.interfaces.exchange_api_interface import OrderResult  # pylint: disable=import-outside-toplevel

        mock_order_result = OrderResult(
            success=True,
            order_id="ORDER123",
            message="Test order",
            error_code=None,
            timestamp="2024-01-01T00:00:00"
        )

        mock_exchange_client.send_order.return_value = mock_order_result

        # Create request
        request_data = {
            "operation": "send_order",
            "parameters": {
                "order_account": "TEST001",
                "item_code": "TXFF4",
                "side": "buy",  # OrderOperation.BUY.value
                "order_type": "Market",  # OrderTypeEnum.Market.value
                "price": 0.0,
                "quantity": 1,
                "open_close": "AUTO",  # OpenClose.AUTO.value
                "note": "Test order",
                "day_trade": "N",  # DayTrade.No.value
                "time_in_force": "IOC",  # TimeInForce.IOC.value
            }
        }

        # Process request
        # pylint: disable=protected-access
        response = gateway_server._process_request(json.dumps(request_data).encode())

        # Verify response format matches unified format
        assert response["success"] is True
        assert response["data"]["is_send_order"] is True
        assert response["data"]["order_serial"] == "ORDER123"
        assert response["data"]["note"] == "Test order"
        assert response["data"]["error_code"] == ""
        assert response["data"]["error_message"] == "Test order"

        # Verify exchange API was called
        mock_exchange_client.send_order.assert_called_once()

    def test_send_order_missing_parameters(self, gateway_server):
        """Test send order request with missing parameters."""
        request_data = {
            "operation": "send_order",
            "parameters": {
                "order_account": "TEST001",
                # Missing required fields
            }
        }

        # pylint: disable=protected-access
        response = gateway_server._process_request(json.dumps(request_data).encode())

        assert response["success"] is False
        assert response["error_code"] == "INVALID_ORDER"
        assert "Missing required fields" in response["error_message"]

    def test_unknown_operation(self, gateway_server):
        """Test handling of unknown operation."""
        request_data = {"operation": "unknown_op"}

        # pylint: disable=protected-access
        response = gateway_server._process_request(json.dumps(request_data).encode())

        assert response["success"] is False
        assert response["error_code"] == "UNKNOWN_OPERATION"

    def test_invalid_json_request(self, gateway_server):
        """Test handling of invalid JSON request."""
        invalid_json = b"{ invalid json }"

        # pylint: disable=protected-access
        response = gateway_server._process_request(invalid_json)

        assert response["success"] is False
        assert response["error_code"] == "INVALID_JSON"
