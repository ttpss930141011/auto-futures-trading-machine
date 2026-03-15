"""Tests for SimulatorExchangeAdapter.

Verifies that the simulator correctly implements ExchangeApiInterface
and can be used for testing without a real exchange connection.
"""

import pytest
from unittest.mock import Mock

from src.domain.interfaces.exchange_api import ExchangeApiInterface
from src.domain.value_objects import (
    OrderOperation,
    OrderTypeEnum,
    TimeInForce,
    OpenClose,
    DayTrade,
)
from src.infrastructure.exchange_adapters.simulator_adapter import SimulatorExchangeAdapter


class TestSimulatorAdapter:
    """Test suite for the simulator exchange adapter."""

    @pytest.fixture
    def simulator(self):
        """Create a simulator adapter instance."""
        return SimulatorExchangeAdapter()

    @pytest.fixture
    def simulator_with_logger(self):
        """Create a simulator with a mock logger."""
        from src.interactor.interfaces.logger.logger import LoggerInterface
        logger = Mock(spec=LoggerInterface)
        return SimulatorExchangeAdapter(logger=logger), logger

    def test_implements_interface(self, simulator):
        """Verify simulator is a valid ExchangeApiInterface."""
        assert isinstance(simulator, ExchangeApiInterface)

    def test_connect(self, simulator):
        """Test connection always succeeds."""
        assert simulator.is_connected is False
        assert simulator.connect() is True
        assert simulator.is_connected is True

    def test_send_order_success(self, simulator):
        """Test order submission returns success."""
        result = simulator.send_order(
            order_account="TEST001",
            item_code="TXFF4",
            side=OrderOperation.BUY,
            order_type=OrderTypeEnum.Market,
            price=18000.0,
            quantity=1,
            open_close=OpenClose.AUTO,
            note="Test order",
            day_trade=DayTrade.No,
            time_in_force=TimeInForce.IOC,
        )

        assert result.is_send_order is True
        assert result.order_serial.startswith("SIM-")
        assert result.error_code == "0"
        assert len(simulator.orders) == 1
        assert simulator.orders[0]["item_code"] == "TXFF4"
        assert simulator.orders[0]["quantity"] == 1

    def test_send_multiple_orders(self, simulator):
        """Test multiple orders are tracked independently."""
        for i in range(3):
            simulator.send_order(
                order_account="TEST001",
                item_code=f"ITEM{i}",
                side=OrderOperation.BUY,
                order_type=OrderTypeEnum.Market,
                price=100.0 + i,
                quantity=1,
                open_close=OpenClose.AUTO,
                note=f"Order {i}",
                day_trade=DayTrade.No,
                time_in_force=TimeInForce.IOC,
            )

        assert len(simulator.orders) == 3
        serials = {o["serial"] for o in simulator.orders}
        assert len(serials) == 3  # unique serials

    def test_get_positions_empty(self, simulator):
        """Test positions are empty by default."""
        assert simulator.get_positions("TEST001") == []

    def test_get_positions_with_filter(self, simulator):
        """Test position filtering by product_id."""
        from src.interactor.dtos.get_position_dtos import PositionDto

        pos1 = PositionDto(investor_account="TEST001", product_id="TXFF4", current_long=1)
        pos2 = PositionDto(investor_account="TEST001", product_id="MXFF4", current_long=2)
        simulator.add_position(pos1)
        simulator.add_position(pos2)

        all_positions = simulator.get_positions("TEST001")
        assert len(all_positions) == 2

        tx_positions = simulator.get_positions("TEST001", "TXFF4")
        assert len(tx_positions) == 1
        assert tx_positions[0].product_id == "TXFF4"

    def test_subscribe_and_inject_tick(self, simulator):
        """Test market data subscription and tick injection."""
        received_ticks = []

        def on_tick(commodity_id, *args):
            received_ticks.append((commodity_id, args[2]))  # price is 3rd arg

        assert simulator.subscribe_market_data("TXFF4", on_tick) is True
        simulator.inject_tick("TXFF4", 18050.0)
        simulator.inject_tick("TXFF4", 18060.0)

        assert len(received_ticks) == 2
        assert received_ticks[0][1] == "18050.0"

    def test_inject_tick_no_subscriber(self, simulator):
        """Test tick injection with no subscribers doesn't crash."""
        simulator.inject_tick("TXFF4", 18000.0)  # Should not raise

    def test_convert_enum_passthrough(self, simulator):
        """Test enum conversion is a pass-through."""
        assert simulator.convert_enum(OrderOperation.BUY) == OrderOperation.BUY
        assert simulator.convert_enum(TimeInForce.IOC) == TimeInForce.IOC

    def test_parse_decimal_passthrough(self, simulator):
        """Test decimal parsing is a pass-through."""
        assert simulator.parse_decimal(18000.0) == 18000.0

    def test_get_client_returns_self(self, simulator):
        """Test get_client returns the simulator itself."""
        assert simulator.get_client() is simulator

    def test_clear_resets_state(self, simulator):
        """Test clear resets all simulator state."""
        simulator.send_order(
            order_account="TEST001",
            item_code="TXFF4",
            side=OrderOperation.BUY,
            order_type=OrderTypeEnum.Market,
            price=18000.0,
            quantity=1,
            open_close=OpenClose.AUTO,
            note="Test",
            day_trade=DayTrade.No,
            time_in_force=TimeInForce.IOC,
        )
        simulator.subscribe_market_data("TXFF4", lambda *a: None)

        assert len(simulator.orders) == 1
        simulator.clear()
        assert len(simulator.orders) == 0
        assert simulator.get_positions("TEST001") == []

    def test_logger_records_events(self, simulator_with_logger):
        """Test logger is called for key events."""
        simulator, logger = simulator_with_logger

        simulator.connect()
        logger.log_info.assert_called_with("Simulator exchange connected")

        simulator.send_order(
            order_account="TEST001",
            item_code="TXFF4",
            side=OrderOperation.BUY,
            order_type=OrderTypeEnum.Market,
            price=18000.0,
            quantity=1,
            open_close=OpenClose.AUTO,
            note="Test",
            day_trade=DayTrade.No,
            time_in_force=TimeInForce.IOC,
        )
        assert logger.log_info.call_count == 2
