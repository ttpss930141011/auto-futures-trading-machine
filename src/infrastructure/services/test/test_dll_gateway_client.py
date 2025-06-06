"""Tests for DLL Gateway Client.

This module contains comprehensive tests for the DLL Gateway Client,
using complete mocking to avoid ZMQ dependencies.
"""

import json
import pytest
from unittest.mock import Mock, MagicMock, patch

from src.infrastructure.services.dll_gateway_client import DllGatewayClient
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.dll_gateway_service_interface import OrderRequest, OrderResponse
from src.interactor.errors.dll_gateway_errors import (
    DllGatewayConnectionError,
    DllGatewayTimeoutError,
    DllGatewayError,
)


class TestDllGatewayClient:
    """Test suite for DLL Gateway Client.
    
    Tests client functionality with complete mocking of ZMQ dependencies.
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
    def mock_context(self):
        """Create mock ZMQ context."""
        return Mock()

    @pytest.fixture
    def mock_socket(self):
        """Create mock ZMQ socket."""
        return Mock()

    @pytest.fixture
    def gateway_client(self, mock_logger, server_address, mock_context, mock_socket):
        """Create DLL Gateway Client instance for testing."""
        with patch('zmq.Context', return_value=mock_context):
            mock_context.socket.return_value = mock_socket
            client = DllGatewayClient(
                server_address=server_address,
                logger=mock_logger,
                timeout_ms=1000,
                retry_count=2,
            )
            client._socket = mock_socket
            return client

    def test_client_initialization(self, mock_logger, server_address):
        """Test client initialization with proper parameters."""
        with patch('zmq.Context'):
            client = DllGatewayClient(
                server_address=server_address,
                logger=mock_logger,
                timeout_ms=1000,
                retry_count=2,
            )
            assert client._server_address == server_address
            assert client._logger == mock_logger
            assert client._timeout_ms == 1000
            assert client._retry_count == 2

    def test_send_order_success(self, gateway_client, mock_socket):
        """Test successful order sending."""
        # Setup mock response
        mock_socket.recv_string.return_value = json.dumps({
            "success": True,
            "order_id": "ORDER123"
        })
        
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
        
        # Verify socket was called
        mock_socket.send_string.assert_called_once()
        mock_socket.recv_string.assert_called_once()

    def test_send_order_failure(self, gateway_client, mock_socket):
        """Test order sending failure from server."""
        # Setup mock response with error
        mock_socket.recv_string.return_value = json.dumps({
            "success": False,
            "error_message": "Invalid order",
            "error_code": "INVALID_ORDER"
        })
        
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

    def test_get_positions_success(self, gateway_client, mock_socket):
        """Test successful position retrieval."""
        # Setup mock response
        mock_socket.recv_string.return_value = json.dumps({
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
        })
        
        positions = gateway_client.get_positions("TEST001")
        
        assert len(positions) == 1
        assert positions[0].account == "TEST001"
        assert positions[0].item_code == "TXFF4"
        assert positions[0].quantity == 5

    def test_get_health_status_success(self, gateway_client, mock_socket):
        """Test successful health status retrieval."""
        # Setup mock response
        mock_socket.recv_string.return_value = json.dumps({
            "success": True,
            "status": "healthy",
            "exchange_connected": True,
            "timestamp": 1234567890
        })
        
        health_status = gateway_client.get_health_status()
        
        assert health_status["status"] == "healthy"
        assert health_status["exchange_connected"] is True
        assert health_status["timestamp"] == 1234567890
        # 'success' should be removed from health status
        assert "success" not in health_status

    def test_is_connected_true(self, gateway_client, mock_socket):
        """Test is_connected returns True when gateway is healthy."""
        # Setup mock response
        mock_socket.recv_string.return_value = json.dumps({
            "success": True,
            "status": "healthy",
            "exchange_connected": True
        })
        
        result = gateway_client.is_connected()
        assert result is True

    def test_is_connected_false(self, gateway_client, mock_socket):
        """Test is_connected returns False when gateway is not connected."""
        # Setup mock response
        mock_socket.recv_string.return_value = json.dumps({
            "success": True,
            "status": "unhealthy",
            "exchange_connected": False
        })
        
        result = gateway_client.is_connected()
        assert result is False

    def test_connection_timeout(self, gateway_client, mock_socket):
        """Test connection timeout handling."""
        # Mock timeout by raising an exception that the client handles
        with patch('src.infrastructure.services.dll_gateway_client.zmq') as mock_zmq:
            class MockAgain(Exception):
                pass
            mock_zmq.Again = MockAgain
            mock_socket.recv_string.side_effect = MockAgain()
            
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

    def test_context_manager(self, mock_logger, server_address):
        """Test client as context manager."""
        with patch('zmq.Context'):
            client = DllGatewayClient(
                server_address=server_address,
                logger=mock_logger,
                timeout_ms=1000,
                retry_count=2,
            )
            with client as c:
                assert c is client
            # Should call close() automatically

    def test_invalid_json_response(self, gateway_client, mock_socket):
        """Test handling of invalid JSON response from server."""
        # Return invalid JSON
        mock_socket.recv_string.return_value = "{ invalid json }"
        
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


class TestDllGatewayClientIntegration:
    """Integration tests for DLL Gateway Client."""

    def test_client_request_response_flow(self, mock_logger):
        """Test complete request-response flow with proper mocking."""
        server_address = "tcp://localhost:15560"
        
        with patch('zmq.Context') as mock_context:
            mock_socket = Mock()
            mock_context.return_value.socket.return_value = mock_socket
            mock_socket.recv_string.return_value = json.dumps({
                "success": True,
                "order_id": "ORDER456",
                "status": "executed"
            })
            
            client = DllGatewayClient(
                server_address=server_address,
                logger=mock_logger,
                timeout_ms=2000,
                retry_count=1
            )
            client._socket = mock_socket
            
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

    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock(spec=LoggerInterface)