"""Tests for DLL Gateway Service interface and data classes.

This module tests the interface definitions and data classes
for the DLL Gateway Service.
"""

import pytest
from dataclasses import asdict
from typing import List
from unittest.mock import MagicMock

from src.interactor.interfaces.services.dll_gateway_service_interface import (
    PositionInfo,
    DllGatewayServiceInterface,
)


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

        class IncompleteImplementation(DllGatewayServiceInterface):
            def send_order(self, input_dto):
                pass
            # Missing other methods

        with pytest.raises(TypeError):
            IncompleteImplementation()

    def test_complete_implementation_works(self):
        """Test that complete implementation can be instantiated."""

        class CompleteImplementation(DllGatewayServiceInterface):
            def send_order(self, input_dto):
                return MagicMock(is_success=True, order_serial="TEST")

            def get_positions(self, account: str) -> List[PositionInfo]:
                return []

            def is_connected(self) -> bool:
                return True

            def get_health_status(self) -> dict:
                return {"status": "healthy"}

        impl = CompleteImplementation()
        assert impl.is_connected() is True
        assert impl.get_health_status()["status"] == "healthy"
        assert impl.get_positions("ANY") == []
