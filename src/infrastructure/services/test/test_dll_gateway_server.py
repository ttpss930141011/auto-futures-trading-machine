"""Tests for DLL Gateway Server.

This module contains comprehensive tests for the DLL Gateway Server,
including functionality, error handling, and integration scenarios.
"""

import json
import pytest
import zmq
import threading
import time
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

from src.infrastructure.services.dll_gateway_server import DllGatewayServer
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.infrastructure.pfcf_client.api import PFCFApi
from src.interactor.errors.dll_gateway_errors import ExchangeApiError


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
        return mock_client

    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock(spec=LoggerInterface)

    @pytest.fixture
    def server_address(self):
        """Provide test server address."""
        return "tcp://127.0.0.1:15557"  # Use different port to avoid conflicts

    @pytest.fixture
    def gateway_server(self, mock_exchange_client, mock_logger, server_address):
        """Create DLL Gateway Server instance for testing."""
        return DllGatewayServer(
            exchange_client=mock_exchange_client,
            logger=mock_logger,
            bind_address=server_address,
            request_timeout_ms=1000,
        )

    def test_server_initialization(self, gateway_server, mock_exchange_client, mock_logger):
        """Test server initialization with proper dependencies."""
        assert gateway_server._exchange_client == mock_exchange_client
        assert gateway_server._logger == mock_logger
        assert gateway_server._context is None
        assert gateway_server._socket is None
        assert gateway_server._running is False

    def test_server_start_success(self, gateway_server, mock_logger):
        """Test successful server startup."""
        try:
            result = gateway_server.start()
            assert result is True
            assert gateway_server._running is True
            assert gateway_server._context is not None
            assert gateway_server._socket is not None
            mock_logger.log_info.assert_called()
        finally:
            gateway_server.stop()

    def test_server_start_already_running(self, gateway_server, mock_logger):
        """Test starting server when already running."""
        try:
            gateway_server.start()
            result = gateway_server.start()  # Try to start again
            assert result is True
            mock_logger.log_warning.assert_called_with("DLL Gateway Server is already running")
        finally:
            gateway_server.stop()

    def test_server_stop(self, gateway_server):
        """Test server graceful shutdown."""
        gateway_server.start()
        assert gateway_server._running is True
        
        gateway_server.stop()
        assert gateway_server._running is False

    def test_context_manager(self, gateway_server):
        """Test server as context manager."""
        with gateway_server as server:
            assert server._running is True
        assert gateway_server._running is False

    def test_send_order_request_processing(self, gateway_server, mock_exchange_client):
        """Test processing of send order requests."""
        # Setup mock
        mock_exchange_client.client.DTradeLib.NewOrder.return_value = "ORDER123"
        
        # Create request
        request_data = {
            "operation": "send_order",
            "parameters": {
                "order_account": "TEST001",
                "item_code": "TXFF4",
                "side": "Buy",
                "order_type": "Market",
                "price": 0.0,
                "quantity": 1,
                "open_close": "AUTO",
                "note": "Test order",
                "day_trade": "No",
                "time_in_force": "IOC",
            }
        }
        
        # Process request
        response = gateway_server._process_request(json.dumps(request_data).encode())
        
        # Verify response
        assert response["success"] is True
        assert response["order_id"] == "ORDER123"
        
        # Verify DLL was called
        mock_exchange_client.client.DTradeLib.NewOrder.assert_called_once_with(
            "TEST001", "TXFF4", "Buy", "Market", 0.0, 1, "AUTO", "Test order", "No", "IOC"
        )

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
        mock_exchange_client.client.DTradeLib.NewOrder.side_effect = Exception("Exchange API error")
        
        request_data = {
            "operation": "send_order",
            "parameters": {
                "order_account": "TEST001",
                "item_code": "TXFF4",
                "side": "Buy",
                "order_type": "Market",
                "price": 0.0,
                "quantity": 1,
                "open_close": "AUTO",
                "note": "Test order",
                "day_trade": "No",
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

    def test_execute_order_success(self, gateway_server, mock_exchange_client):
        """Test successful order execution."""
        from src.interactor.interfaces.services.dll_gateway_service_interface import OrderRequest
        
        mock_exchange_client.client.DTradeLib.NewOrder.return_value = "ORDER123"
        
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
        
        response = gateway_server._execute_order(order_request)
        
        assert response.success is True
        assert response.order_id == "ORDER123"

    def test_execute_order_failure(self, gateway_server, mock_exchange_client):
        """Test order execution failure."""
        from src.interactor.interfaces.services.dll_gateway_service_interface import OrderRequest
        
        mock_exchange_client.client.DTradeLib.NewOrder.return_value = None
        
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
        
        response = gateway_server._execute_order(order_request)
        
        assert response.success is False
        assert response.error_code == "EXECUTION_FAILED"


class TestDllGatewayServerIntegration:
    """Integration tests for DLL Gateway Server.
    
    Tests actual ZeroMQ communication and server lifecycle.
    """

    @pytest.fixture
    def integration_server_address(self):
        """Provide integration test server address."""
        return "tcp://127.0.0.1:15558"

    def test_zmq_communication(self, mock_exchange_client, mock_logger, integration_server_address):
        """Test actual ZeroMQ communication with server."""
        server = DllGatewayServer(
            exchange_client=mock_exchange_client,
            logger=mock_logger,
            bind_address=integration_server_address,
            request_timeout_ms=1000,
        )
        
        try:
            # Start server
            assert server.start() is True
            time.sleep(0.1)  # Give server time to start
            
            # Create client
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.setsockopt(zmq.RCVTIMEO, 2000)
            socket.setsockopt(zmq.SNDTIMEO, 2000)
            socket.connect(integration_server_address.replace("*", "localhost"))
            
            # Send health check request
            request = {"operation": "health_check"}
            socket.send_string(json.dumps(request))
            
            # Receive response
            response_str = socket.recv_string()
            response = json.loads(response_str)
            
            assert response["success"] is True
            assert response["status"] == "healthy"
            
            socket.close()
            context.term()
            
        finally:
            server.stop()

    def test_server_lifecycle_with_multiple_requests(self, mock_exchange_client, mock_logger, integration_server_address):
        """Test server handling multiple requests over its lifecycle."""
        server = DllGatewayServer(
            exchange_client=mock_exchange_client,
            logger=mock_logger,
            bind_address=integration_server_address,
            request_timeout_ms=1000,
        )
        
        try:
            server.start()
            time.sleep(0.1)
            
            # Send multiple health check requests
            for i in range(3):
                context = zmq.Context()
                socket = context.socket(zmq.REQ)
                socket.setsockopt(zmq.RCVTIMEO, 2000)
                socket.connect(integration_server_address.replace("*", "localhost"))
                
                request = {"operation": "health_check"}
                socket.send_string(json.dumps(request))
                response_str = socket.recv_string()
                response = json.loads(response_str)
                
                assert response["success"] is True
                
                socket.close()
                context.term()
                
        finally:
            server.stop()