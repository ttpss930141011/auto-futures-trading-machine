"""Tests for DLL Gateway Service interface and data classes.

This module tests the interface definitions and data classes
for the DLL Gateway Service.
"""

import pytest
from dataclasses import asdict
from typing import List

from src.interactor.interfaces.services.dll_gateway_service_interface import (
    OrderRequest,
    OrderResponse,
    PositionInfo,
    DllGatewayServiceInterface,
)


class TestOrderRequest:
    """Test suite for OrderRequest data class."""

    def test_order_request_creation(self):
        """Test OrderRequest creation with all fields."""
        order_request = OrderRequest(
            order_account="TEST001",
            item_code="TXFF4",
            side="Buy",
            order_type="Market",
            price=15000.0,
            quantity=2,
            open_close="AUTO",
            note="Test order",
            day_trade="No",
            time_in_force="IOC"
        )
        
        assert order_request.order_account == "TEST001"
        assert order_request.item_code == "TXFF4"
        assert order_request.side == "Buy"
        assert order_request.order_type == "Market"
        assert order_request.price == 15000.0
        assert order_request.quantity == 2
        assert order_request.open_close == "AUTO"
        assert order_request.note == "Test order"
        assert order_request.day_trade == "No"
        assert order_request.time_in_force == "IOC"

    def test_order_request_as_dict(self):
        """Test OrderRequest conversion to dictionary."""
        order_request = OrderRequest(
            order_account="TEST001",
            item_code="TXFF4",
            side="Sell",
            order_type="Limit",
            price=14500.0,
            quantity=1,
            open_close="Open",
            note="Limit order",
            day_trade="Yes",
            time_in_force="FOK"
        )
        
        order_dict = asdict(order_request)
        
        assert order_dict["order_account"] == "TEST001"
        assert order_dict["item_code"] == "TXFF4"
        assert order_dict["side"] == "Sell"
        assert order_dict["order_type"] == "Limit"
        assert order_dict["price"] == 14500.0
        assert order_dict["quantity"] == 1
        assert order_dict["open_close"] == "Open"
        assert order_dict["note"] == "Limit order"
        assert order_dict["day_trade"] == "Yes"
        assert order_dict["time_in_force"] == "FOK"

    def test_order_request_equality(self):
        """Test OrderRequest equality comparison."""
        order1 = OrderRequest(
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
        
        order2 = OrderRequest(
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
        
        order3 = OrderRequest(
            order_account="TEST002",  # Different account
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
        
        assert order1 == order2
        assert order1 != order3


class TestOrderResponse:
    """Test suite for OrderResponse data class."""

    def test_order_response_success(self):
        """Test OrderResponse for successful order."""
        response = OrderResponse(
            success=True,
            order_id="ORDER123"
        )
        
        assert response.success is True
        assert response.order_id == "ORDER123"
        assert response.error_message is None
        assert response.error_code is None

    def test_order_response_failure(self):
        """Test OrderResponse for failed order."""
        response = OrderResponse(
            success=False,
            error_message="Insufficient funds",
            error_code="INSUFFICIENT_FUNDS"
        )
        
        assert response.success is False
        assert response.order_id is None
        assert response.error_message == "Insufficient funds"
        assert response.error_code == "INSUFFICIENT_FUNDS"

    def test_order_response_as_dict(self):
        """Test OrderResponse conversion to dictionary."""
        response = OrderResponse(
            success=True,
            order_id="ORDER456",
            error_message=None,
            error_code=None
        )
        
        response_dict = asdict(response)
        
        assert response_dict["success"] is True
        assert response_dict["order_id"] == "ORDER456"
        assert response_dict["error_message"] is None
        assert response_dict["error_code"] is None


class TestPositionInfo:
    """Test suite for PositionInfo data class."""

    def test_position_info_creation(self):
        """Test PositionInfo creation with all fields."""
        position = PositionInfo(
            account="TEST001",
            item_code="TXFF4",
            quantity=5,
            average_price=15200.0,
            unrealized_pnl=2500.0
        )
        
        assert position.account == "TEST001"
        assert position.item_code == "TXFF4"
        assert position.quantity == 5
        assert position.average_price == 15200.0
        assert position.unrealized_pnl == 2500.0

    def test_position_info_negative_values(self):
        """Test PositionInfo with negative values."""
        position = PositionInfo(
            account="TEST002",
            item_code="TXFF4",
            quantity=-3,  # Short position
            average_price=14800.0,
            unrealized_pnl=-1200.0  # Loss
        )
        
        assert position.quantity == -3
        assert position.unrealized_pnl == -1200.0

    def test_position_info_as_dict(self):
        """Test PositionInfo conversion to dictionary."""
        position = PositionInfo(
            account="TEST003",
            item_code="MXFF4",
            quantity=10,
            average_price=5100.0,
            unrealized_pnl=500.0
        )
        
        position_dict = asdict(position)
        
        assert position_dict["account"] == "TEST003"
        assert position_dict["item_code"] == "MXFF4"
        assert position_dict["quantity"] == 10
        assert position_dict["average_price"] == 5100.0
        assert position_dict["unrealized_pnl"] == 500.0


class TestDllGatewayServiceInterface:
    """Test suite for DLL Gateway Service interface."""

    def test_interface_is_abstract(self):
        """Test that the interface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DllGatewayServiceInterface()

    def test_interface_methods_are_abstract(self):
        """Test that interface methods are properly marked as abstract."""
        # Get all abstract methods
        abstract_methods = DllGatewayServiceInterface.__abstractmethods__
        
        expected_methods = {
            'send_order',
            'get_positions',
            'is_connected',
            'get_health_status'
        }
        
        assert abstract_methods == expected_methods

    def test_concrete_implementation_requirements(self):
        """Test that concrete implementations must implement all methods."""
        
        # Create incomplete implementation
        class IncompleteImplementation(DllGatewayServiceInterface):
            def send_order(self, order_request):
                pass
            # Missing other methods
        
        # Should not be able to instantiate
        with pytest.raises(TypeError):
            IncompleteImplementation()

    def test_complete_implementation_works(self):
        """Test that complete implementation can be instantiated."""
        
        class CompleteImplementation(DllGatewayServiceInterface):
            def send_order(self, order_request: OrderRequest) -> OrderResponse:
                return OrderResponse(success=True, order_id="TEST")
            
            def get_positions(self, account: str) -> List[PositionInfo]:
                return []
            
            def is_connected(self) -> bool:
                return True
            
            def get_health_status(self) -> dict:
                return {"status": "healthy"}
        
        # Should be able to instantiate and use
        impl = CompleteImplementation()
        assert impl.is_connected() is True
        assert impl.get_health_status()["status"] == "healthy"
        
        # Test send_order
        order_request = OrderRequest(
            order_account="TEST",
            item_code="TEST",
            side="Buy",
            order_type="Market",
            price=0.0,
            quantity=1,
            open_close="AUTO",
            note="Test",
            day_trade="No",
            time_in_force="IOC"
        )
        response = impl.send_order(order_request)
        assert response.success is True
        assert response.order_id == "TEST"


class TestDataClassesIntegration:
    """Integration tests for data classes working together."""

    def test_order_request_to_response_flow(self):
        """Test typical flow from order request to response."""
        # Create order request
        order_request = OrderRequest(
            order_account="INTEGRATION_TEST",
            item_code="TXFF4",
            side="Buy",
            order_type="Market",
            price=0.0,
            quantity=3,
            open_close="AUTO",
            note="Integration test",
            day_trade="No",
            time_in_force="IOC"
        )
        
        # Simulate successful response
        success_response = OrderResponse(
            success=True,
            order_id="INTEGRATION_ORDER_123"
        )
        
        # Simulate failed response
        failure_response = OrderResponse(
            success=False,
            error_message="Market is closed",
            error_code="MARKET_CLOSED"
        )
        
        # Verify both responses are valid
        assert success_response.success is True
        assert success_response.order_id == "INTEGRATION_ORDER_123"
        
        assert failure_response.success is False
        assert failure_response.error_code == "MARKET_CLOSED"

    def test_position_list_handling(self):
        """Test handling of multiple positions."""
        positions = [
            PositionInfo(
                account="TEST001",
                item_code="TXFF4",
                quantity=2,
                average_price=15000.0,
                unrealized_pnl=400.0
            ),
            PositionInfo(
                account="TEST001",
                item_code="MXFF4",
                quantity=-1,
                average_price=5200.0,
                unrealized_pnl=-150.0
            )
        ]
        
        # Verify list operations
        assert len(positions) == 2
        assert positions[0].quantity > 0  # Long position
        assert positions[1].quantity < 0  # Short position
        
        # Calculate total PnL
        total_pnl = sum(pos.unrealized_pnl for pos in positions)
        assert total_pnl == 250.0  # 400.0 + (-150.0)