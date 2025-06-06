"""Tests for DLL Gateway Client.

This module contains comprehensive tests for the DLL Gateway Client,
including communication, error handling, and retry mechanisms.
"""

import json
import pytest
import zmq
import threading
import time
from unittest.mock import Mock, MagicMock, patch

from src.infrastructure.services.dll_gateway_client import DllGatewayClient
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.dll_gateway_service_interface import OrderRequest, OrderResponse
from src.interactor.errors.dll_gateway_errors import (
    DllGatewayConnectionError,
    DllGatewayTimeoutError,
    DllGatewayError,
)


class MockZmqServer:
    """Mock ZeroMQ server for testing client communication."""

    def __init__(self, bind_address: str, response_data: dict = None):
        self.bind_address = bind_address
        self.response_data = response_data or {"success": True, "status": "healthy"}
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.running = False
        self.thread = None

    def start(self):
        """Start the mock server."""
        self.socket.bind(self.bind_address)
        self.running = True
        self.thread = threading.Thread(target=self._run_server)
        self.thread.daemon = True
        self.thread.start()
        time.sleep(0.1)  # Give server time to start

    def stop(self):
        """Stop the mock server."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.socket.close()
        self.context.term()

    def _run_server(self):
        """Run the mock server loop."""
        while self.running:
            try:
                # Receive request with timeout
                self.socket.setsockopt(zmq.RCVTIMEO, 100)
                request = self.socket.recv_string(zmq.NOBLOCK)
                
                # Send response
                self.socket.send_string(json.dumps(self.response_data))
                
            except zmq.Again:
                continue
            except zmq.ZMQError:
                break


class TestDllGatewayClient:
    """Test suite for DLL Gateway Client.
    
    Tests client functionality, communication, error handling,
    and retry mechanisms.
    """

    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock(spec=LoggerInterface)

    @pytest.fixture
    def server_address(self):
        """Provide test server address."""
        return "tcp://localhost:15559"

    @pytest.fixture
    def gateway_client(self, mock_logger, server_address):
        """Create DLL Gateway Client instance for testing."""
        return DllGatewayClient(
            server_address=server_address,
            logger=mock_logger,
            timeout_ms=1000,
            retry_count=2,
        )

    def test_client_initialization(self, gateway_client, mock_logger, server_address):
        """Test client initialization with proper parameters."""
        assert gateway_client._server_address == server_address
        assert gateway_client._logger == mock_logger
        assert gateway_client._timeout_ms == 1000
        assert gateway_client._retry_count == 2
        assert gateway_client._socket is None
        assert gateway_client._connected is False

    def test_send_order_success(self, gateway_client, server_address):
        """Test successful order sending."""
        # Setup mock server
        response_data = {
            "success": True,
            "order_id": "ORDER123"
        }
        mock_server = MockZmqServer(server_address.replace("localhost", "*"), response_data)
        
        try:
            mock_server.start()
            
            # Create order request
            order_request = OrderRequest(
                order_account="TEST001",
                item_code="TXFF4",
                side="Buy",
                order_type="Market",
                price=0.0,
                quantity=1,
                open_close="AUTO",
                note="Test order",
                day_trade="No",
                time_in_force="IOC"
            )
            
            # Send order
            response = gateway_client.send_order(order_request)
            
            # Verify response
            assert isinstance(response, OrderResponse)
            assert response.success is True
            assert response.order_id == "ORDER123"
            
        finally:
            mock_server.stop()
            gateway_client.close()

    def test_send_order_failure(self, gateway_client, server_address):
        """Test order sending failure from server."""
        # Setup mock server with error response
        response_data = {
            "success": False,
            "error_message": "Invalid order",
            "error_code": "INVALID_ORDER"
        }
        mock_server = MockZmqServer(server_address.replace("localhost", "*"), response_data)
        
        try:
            mock_server.start()
            
            order_request = OrderRequest(
                order_account="TEST001",
                item_code="TXFF4",
                side="Buy",
                order_type="Market",
                price=0.0,
                quantity=1,
                open_close="AUTO",
                note="Test order",
                day_trade="No",
                time_in_force="IOC"
            )
            
            # This should raise an exception because server returned error
            with pytest.raises(DllGatewayError) as exc_info:
                gateway_client.send_order(order_request)
            
            assert "Invalid order" in str(exc_info.value)
            
        finally:
            mock_server.stop()
            gateway_client.close()

    def test_get_positions_success(self, gateway_client, server_address):
        """Test successful position retrieval."""
        response_data = {
            "success": True,
            "positions": [
                {
                    "account": "TEST001",
                    "item_code": "TXFF4",
                    "quantity": 5,
                    "average_price": 15000.0,
                    "unrealized_pnl": 1000.0
                }
            ]
        }
        mock_server = MockZmqServer(server_address.replace("localhost", "*"), response_data)
        
        try:
            mock_server.start()
            
            positions = gateway_client.get_positions("TEST001")
            
            assert len(positions) == 1
            assert positions[0].account == "TEST001"
            assert positions[0].item_code == "TXFF4"
            assert positions[0].quantity == 5
            
        finally:
            mock_server.stop()
            gateway_client.close()

    def test_get_health_status_success(self, gateway_client, server_address):
        """Test successful health status retrieval."""
        response_data = {
            "success": True,
            "status": "healthy",
            "exchange_connected": True,
            "timestamp": 1234567890
        }
        mock_server = MockZmqServer(server_address.replace("localhost", "*"), response_data)
        
        try:
            mock_server.start()
            
            health_status = gateway_client.get_health_status()
            
            assert health_status["status"] == "healthy"
            assert health_status["exchange_connected"] is True
            assert health_status["timestamp"] == 1234567890
            # 'success' should be removed from health status
            assert "success" not in health_status
            
        finally:
            mock_server.stop()
            gateway_client.close()

    def test_is_connected_true(self, gateway_client, server_address):
        """Test is_connected returns True when gateway is healthy."""
        response_data = {
            "success": True,
            "status": "healthy",
            "exchange_connected": True
        }
        mock_server = MockZmqServer(server_address.replace("localhost", "*"), response_data)
        
        try:
            mock_server.start()
            
            result = gateway_client.is_connected()
            assert result is True
            
        finally:
            mock_server.stop()
            gateway_client.close()

    def test_is_connected_false(self, gateway_client, server_address):
        """Test is_connected returns False when gateway is not connected."""
        response_data = {
            "success": True,
            "status": "unhealthy",
            "exchange_connected": False
        }
        mock_server = MockZmqServer(server_address.replace("localhost", "*"), response_data)
        
        try:
            mock_server.start()
            
            result = gateway_client.is_connected()
            assert result is False
            
        finally:
            mock_server.stop()
            gateway_client.close()

    def test_connection_timeout(self, gateway_client):
        """Test connection timeout handling."""
        # No server running, should timeout
        order_request = OrderRequest(
            order_account="TEST001",
            item_code="TXFF4",
            side="Buy",
            order_type="Market",
            price=0.0,
            quantity=1,
            open_close="AUTO",
            note="Test order",
            day_trade="No",
            time_in_force="IOC"
        )
        
        with pytest.raises(DllGatewayTimeoutError):
            gateway_client.send_order(order_request)

    def test_retry_mechanism(self, gateway_client, mock_logger):
        """Test retry mechanism on connection failures."""
        # Mock the socket to simulate failures
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_socket.send_string.side_effect = [zmq.Again(), zmq.Again(), None]
            mock_socket.recv_string.return_value = json.dumps({"success": True})
            mock_context.return_value.socket.return_value = mock_socket
            
            order_request = OrderRequest(
                order_account="TEST001",
                item_code="TXFF4",
                side="Buy",
                order_type="Market",
                price=0.0,
                quantity=1,
                open_close="AUTO",
                note="Test order",
                day_trade="No",
                time_in_force="IOC"
            )
            
            # Should succeed after retries
            response = gateway_client.send_order(order_request)
            assert response.success is True
            
            # Verify retry attempts were logged
            assert mock_logger.log_warning.call_count >= 2

    def test_context_manager(self, gateway_client):
        """Test client as context manager."""
        with gateway_client as client:
            assert client is gateway_client
        # Should call close() automatically

    def test_connection_reset_on_error(self, gateway_client):
        """Test connection reset on ZMQ errors."""
        # Mock the socket to simulate ZMQ error
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_socket.send_string.side_effect = zmq.ZMQError("Connection failed")
            mock_context.return_value.socket.return_value = mock_socket
            
            order_request = OrderRequest(
                order_account="TEST001",
                item_code="TXFF4",
                side="Buy",
                order_type="Market",
                price=0.0,
                quantity=1,
                open_close="AUTO",
                note="Test order",
                day_trade="No",
                time_in_force="IOC"
            )
            
            with pytest.raises(DllGatewayConnectionError):
                gateway_client.send_order(order_request)

    def test_invalid_json_response(self, gateway_client, server_address):
        """Test handling of invalid JSON response from server."""
        # Setup mock server that returns invalid JSON
        invalid_response_server = MockZmqServer(
            server_address.replace("localhost", "*"),
            response_data="invalid json"  # This will be sent as string, not JSON
        )
        
        # Override the server's response method to send invalid JSON
        def send_invalid_json():
            invalid_response_server.socket.send_string("{ invalid json }")
        
        try:
            invalid_response_server.start()
            
            order_request = OrderRequest(
                order_account="TEST001",
                item_code="TXFF4",
                side="Buy",
                order_type="Market",
                price=0.0,
                quantity=1,
                open_close="AUTO",
                note="Test order",
                day_trade="No",
                time_in_force="IOC"
            )
            
            with pytest.raises(DllGatewayError) as exc_info:
                gateway_client.send_order(order_request)
            
            assert "Invalid JSON response" in str(exc_info.value)
            
        finally:
            invalid_response_server.stop()
            gateway_client.close()


class TestDllGatewayClientIntegration:
    """Integration tests for DLL Gateway Client."""

    def test_client_server_communication_flow(self):
        """Test complete communication flow between client and mock server."""
        server_address = "tcp://localhost:15560"
        
        # Setup mock server
        response_data = {
            "success": True,
            "order_id": "ORDER456",
            "status": "executed"
        }
        mock_server = MockZmqServer(server_address.replace("localhost", "*"), response_data)
        
        # Setup client
        mock_logger = Mock(spec=LoggerInterface)
        client = DllGatewayClient(
            server_address=server_address,
            logger=mock_logger,
            timeout_ms=2000,
            retry_count=1
        )
        
        try:
            mock_server.start()
            
            # Test order sending
            order_request = OrderRequest(
                order_account="INTEGRATION_TEST",
                item_code="TXFF4",
                side="Sell",
                order_type="Market",
                price=0.0,
                quantity=2,
                open_close="AUTO",
                note="Integration test order",
                day_trade="No",
                time_in_force="IOC"
            )
            
            response = client.send_order(order_request)
            
            assert response.success is True
            assert response.order_id == "ORDER456"
            
            # Verify logging
            mock_logger.log_info.assert_called()
            
        finally:
            mock_server.stop()
            client.close()