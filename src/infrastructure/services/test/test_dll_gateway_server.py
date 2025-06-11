"""Tests for DLL Gateway Server.

This module contains comprehensive tests for the DLL Gateway Server,
including functionality, error handling, and integration scenarios.
"""

import json
import pytest
from unittest.mock import Mock, patch

from src.infrastructure.services.dll_gateway_server import DllGatewayServer
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infrastructure.pfcf_client.api import PFCFApi


class TestDllGatewayServer:
    """Test suite for DLL Gateway Server.

    Tests server functionality, request processing, error handling,
    and integration with ZeroMQ and exchange API.
    """

    @pytest.fixture
    def mock_exchange_client(self):
        """Create mock exchange client."""
        mock_client = Mock(spec=PFCFApi)
        mock_client.client = Mock()
        mock_client.client.DTradeLib = Mock()
        mock_client.client.DAccountLib = Mock()

        # Add trade attribute for OrderObject
        mock_client.trade = Mock()
        mock_client.trade.OrderObject = Mock()

        # Add decimal attribute for EnumConverter
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
        from src.app.cli_pfcf.config import Config
        return Mock(spec=Config)

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
            assert gateway_server._running is True

            gateway_server.stop()
            assert gateway_server._running is False

    def test_context_manager(self, gateway_server):
        """Test server as context manager."""
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_context.return_value.socket.return_value = mock_socket

            with gateway_server as server:
                assert server._running is True
            assert gateway_server._running is False

    def test_send_order_request_processing(self, gateway_server, mock_exchange_client, mock_config):
        """Test processing of send order requests."""
        # Setup mock order result
        mock_order_result = Mock()
        mock_order_result.ISSEND = True
        mock_order_result.NOTE = "Test order"
        mock_order_result.SEQ = "ORDER123"
        mock_order_result.ERRORCODE = 0
        mock_order_result.ERRORMSG = ""

        mock_exchange_client.client.DTradeLib.Order.return_value = mock_order_result

        # Setup mock config for to_pfcf_dict
        mock_config_instance = Mock()
        mock_config_instance.to_pfcf_dict.return_value = {
            "ACTNO": "TEST001",
            "PRODUCTID": "TXFF4",
            "BS": "Buy",
            "ORDERTYPE": "Market",
            "PRICE": 0.0,
            "ORDERQTY": 1,
            "TIMEINFORCE": "IOC",
            "OPENCLOSE": "AUTO",
            "DTRADE": "No",
            "NOTE": "Test order"
        }

        # Create request
        request_data = {
            "operation": "send_order",
            "parameters": {
                "order_account": "TEST001",
                "item_code": "TXFF4",
                "side": "buy",  # Use correct OrderOperation value
                "order_type": "Market",
                "price": 0.0,
                "quantity": 1,
                "open_close": "AUTO",
                "note": "Test order",
                "day_trade": "N",  # Use correct DayTrade value
                "time_in_force": "IOC",
            }
        }

        # Process request
        response = gateway_server._process_request(json.dumps(request_data).encode())

        # Verify response format matches SendMarketOrderOutputDto
        assert response["is_send_order"] is True
        assert response["order_serial"] == "ORDER123"
        assert response["note"] == "Test order"
        assert response["error_code"] == "0"
        assert response["error_message"] == ""

        # Verify DLL was called
        mock_exchange_client.client.DTradeLib.Order.assert_called_once()

    def test_send_order_missing_parameters(self, gateway_server):
        """Test send order request with missing parameters."""
        request_data = {
            "operation": "send_order",
            "parameters": {
                "order_account": "TEST001",
                # Missing required fields
            }
        }

        response = gateway_server._process_request(json.dumps(request_data).encode())

        assert response["success"] is False
        assert response["error_code"] == "INVALID_ORDER"
        assert "Missing required fields" in response["error_message"]

    def test_send_order_exchange_error(self, gateway_server, mock_exchange_client):
        """Test send order when exchange API raises error."""
        # Setup mock to raise exception
        mock_exchange_client.client.DTradeLib.Order.side_effect = Exception("Exchange API error")

        request_data = {
            "operation": "send_order",
            "parameters": {
                "order_account": "TEST001",
                "item_code": "TXFF4",
                "side": "buy",  # Use correct OrderOperation value
                "order_type": "Market",
                "price": 0.0,
                "quantity": 1,
                "open_close": "AUTO",
                "note": "Test order",
                "day_trade": "N",  # Use correct DayTrade value
                "time_in_force": "IOC",
            }
        }

        response = gateway_server._process_request(json.dumps(request_data).encode())

        assert response["success"] is False
        assert response["error_code"] == "ORDER_EXECUTION_ERROR"

    def test_get_positions_request(self, gateway_server):
        """Test get positions request processing."""
        request_data = {
            "operation": "get_positions",
            "parameters": {"account": "TEST001"}
        }

        response = gateway_server._process_request(json.dumps(request_data).encode())

        # Note: Current implementation returns empty list
        assert response["success"] is True
        assert response["positions"] == []

    def test_get_positions_missing_account(self, gateway_server):
        """Test get positions request without account parameter."""
        request_data = {
            "operation": "get_positions",
            "parameters": {}
        }

        response = gateway_server._process_request(json.dumps(request_data).encode())

        assert response["success"] is False
        assert response["error_code"] == "MISSING_ACCOUNT"

    def test_health_check_request(self, gateway_server, mock_exchange_client):
        """Test health check request processing."""
        request_data = {"operation": "health_check"}

        response = gateway_server._process_request(json.dumps(request_data).encode())

        assert response["success"] is True
        assert response["status"] == "healthy"
        assert response["exchange_connected"] is True
        assert "timestamp" in response

    def test_unknown_operation(self, gateway_server):
        """Test handling of unknown operation."""
        request_data = {"operation": "unknown_op"}

        response = gateway_server._process_request(json.dumps(request_data).encode())

        assert response["success"] is False
        assert response["error_code"] == "UNKNOWN_OPERATION"

    def test_invalid_json_request(self, gateway_server):
        """Test handling of invalid JSON request."""
        invalid_json = b"{ invalid json }"

        response = gateway_server._process_request(invalid_json)

        assert response["success"] is False
        assert response["error_code"] == "INVALID_JSON"

    def test_request_processing_exception(self, gateway_server, mock_logger):
        """Test handling of unexpected exceptions during request processing."""
        # This will cause an exception because we're passing invalid data
        with patch.object(gateway_server, '_handle_send_order', side_effect=Exception("Test error")):
            request_data = {
                "operation": "send_order",
                "parameters": {}
            }

            response = gateway_server._process_request(json.dumps(request_data).encode())

            assert response["success"] is False
            assert response["error_code"] == "PROCESSING_ERROR"

    def test_execute_order_success(self, gateway_server, mock_exchange_client, mock_config):
        """Test successful order execution."""
        from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto
        from src.domain.value_objects import OrderOperation, OrderTypeEnum, OpenClose, DayTrade, TimeInForce

        # Setup mock order result
        mock_order_result = Mock()
        mock_order_result.ISSEND = True
        mock_order_result.NOTE = "Test"
        mock_order_result.SEQ = "ORDER123"
        mock_order_result.ERRORCODE = 0
        mock_order_result.ERRORMSG = ""

        mock_exchange_client.client.DTradeLib.Order.return_value = mock_order_result

        input_dto = SendMarketOrderInputDto(
            order_account="TEST001",
            item_code="TXFF4",
            side=OrderOperation.BUY,
            order_type=OrderTypeEnum.Market,
            price=0.0,
            quantity=1,
            open_close=OpenClose.AUTO,
            note="Test",
            day_trade=DayTrade.No,
            time_in_force=TimeInForce.IOC
        )

        response = gateway_server._execute_order(input_dto)

        assert response.is_send_order is True
        assert response.order_serial == "ORDER123"

    def test_execute_order_failure(self, gateway_server, mock_exchange_client, mock_config):
        """Test order execution failure."""
        from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto
        from src.domain.value_objects import OrderOperation, OrderTypeEnum, OpenClose, DayTrade, TimeInForce

        mock_exchange_client.client.DTradeLib.Order.return_value = None

        input_dto = SendMarketOrderInputDto(
            order_account="TEST001",
            item_code="TXFF4",
            side=OrderOperation.BUY,
            order_type=OrderTypeEnum.Market,
            price=0.0,
            quantity=1,
            open_close=OpenClose.AUTO,
            note="Test",
            day_trade=DayTrade.No,
            time_in_force=TimeInForce.IOC
        )

        response = gateway_server._execute_order(input_dto)

        assert response.is_send_order is False
        assert response.error_code == "NULL_RESULT"


class TestDllGatewayServerIntegration:
    """Integration tests for DLL Gateway Server.

    Tests actual ZeroMQ communication and server lifecycle.
    """

    @pytest.fixture
    def mock_exchange_client(self):
        """Create mock exchange client."""
        mock_client = Mock(spec=PFCFApi)
        mock_client.client = Mock()
        mock_client.client.DTradeLib = Mock()
        mock_client.client.DAccountLib = Mock()

        # Add trade attribute for OrderObject
        mock_client.trade = Mock()
        mock_client.trade.OrderObject = Mock()

        # Add decimal attribute for EnumConverter
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
        from src.app.cli_pfcf.config import Config
        return Mock(spec=Config)

    @pytest.fixture
    def integration_server_address(self):
        """Provide integration test server address."""
        return "tcp://127.0.0.1:15558"

    def test_zmq_communication(self, mock_exchange_client, mock_config, mock_logger, integration_server_address):
        """Test ZeroMQ communication with server using mocks."""
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_context.return_value.socket.return_value = mock_socket

            server = DllGatewayServer(
                exchange_client=mock_exchange_client,
                config=mock_config,
                logger=mock_logger,
                bind_address=integration_server_address,
                request_timeout_ms=1000,
            )

            # Start server
            assert server.start() is True

            # Mock a health check request
            request = {"operation": "health_check"}
            response = server._process_request(json.dumps(request).encode())

            assert response["success"] is True
            assert response["status"] == "healthy"

    def test_server_lifecycle_with_multiple_requests(self, mock_exchange_client, mock_config, mock_logger, integration_server_address):
        """Test server handling multiple requests over its lifecycle."""
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_context.return_value.socket.return_value = mock_socket

            server = DllGatewayServer(
                exchange_client=mock_exchange_client,
                config=mock_config,
                logger=mock_logger,
                bind_address=integration_server_address,
                request_timeout_ms=1000,
            )

            server.start()

            # Send multiple health check requests
            for i in range(3):
                request = {"operation": "health_check"}
                response = server._process_request(json.dumps(request).encode())
                assert response["success"] is True
