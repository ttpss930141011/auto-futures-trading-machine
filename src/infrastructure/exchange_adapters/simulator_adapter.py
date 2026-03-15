"""Simulator Exchange Adapter.

A lightweight exchange simulator for testing and development,
implementing ExchangeApiInterface without requiring any DLL or
external exchange connection.

Usage:
    adapter = SimulatorExchangeAdapter()
    adapter.connect()
    result = adapter.send_order(...)
"""

import uuid
from typing import Any, Callable, List

from src.domain.interfaces.exchange_api import ExchangeApiInterface
from src.domain.value_objects import (
    OrderOperation,
    OrderTypeEnum,
    TimeInForce,
    OpenClose,
    DayTrade,
)
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderOutputDto
from src.interactor.dtos.get_position_dtos import PositionDto
from src.interactor.interfaces.logger.logger import LoggerInterface


class SimulatorExchangeAdapter(ExchangeApiInterface):
    """In-memory exchange simulator for testing without a real exchange.

    All orders are accepted and tracked in memory. Market data can be
    fed manually via ``inject_tick`` for strategy testing.
    """

    def __init__(self, logger: LoggerInterface | None = None) -> None:
        """Initialize the simulator.

        Args:
            logger: Optional logger for recording simulated events.
        """
        self._logger = logger
        self._connected = False
        self._orders: List[dict] = []
        self._positions: List[PositionDto] = []
        self._market_data_callbacks: dict[str, List[Callable]] = {}

    # ------------------------------------------------------------------ #
    #  ExchangeApiInterface implementation                                #
    # ------------------------------------------------------------------ #

    def connect(self, **credentials) -> bool:
        """Simulate exchange connection (always succeeds).

        Args:
            **credentials: Ignored in simulator mode.

        Returns:
            Always True.
        """
        self._connected = True
        if self._logger:
            self._logger.log_info("Simulator exchange connected")
        return True

    def send_order(
        self,
        order_account: str,
        item_code: str,
        side: OrderOperation,
        order_type: OrderTypeEnum,
        price: float,
        quantity: int,
        open_close: OpenClose,
        note: str,
        day_trade: DayTrade,
        time_in_force: TimeInForce,
    ) -> SendMarketOrderOutputDto:
        """Simulate order execution.

        All orders are accepted and stored in the internal order list.

        Args:
            order_account: Trading account identifier.
            item_code: Product/commodity code.
            side: Buy or sell operation.
            order_type: Market, limit, or market price order.
            price: Order price.
            quantity: Order quantity.
            open_close: Open or close position.
            note: Order note/reference.
            day_trade: Day trade flag.
            time_in_force: Time in force setting.

        Returns:
            SendMarketOrderOutputDto indicating success.
        """
        order_serial = f"SIM-{uuid.uuid4().hex[:8].upper()}"

        order_record = {
            "serial": order_serial,
            "account": order_account,
            "item_code": item_code,
            "side": side.value,
            "order_type": order_type.value,
            "price": price,
            "quantity": quantity,
            "open_close": open_close.value,
            "note": note,
            "day_trade": day_trade.value,
            "time_in_force": time_in_force.value,
        }
        self._orders.append(order_record)

        if self._logger:
            self._logger.log_info(
                f"Simulator order: {side.value} {quantity}x {item_code} "
                f"@ {price} [{order_serial}]"
            )

        return SendMarketOrderOutputDto(
            is_send_order=True,
            note=note,
            order_serial=order_serial,
            error_code="0",
            error_message="",
        )

    def get_positions(self, account: str, product_id: str = "") -> List[PositionDto]:
        """Return simulated positions.

        Args:
            account: Trading account identifier.
            product_id: Optional product filter.

        Returns:
            List of simulated position DTOs.
        """
        if product_id:
            return [p for p in self._positions if p.product_id == product_id]
        return list(self._positions)

    def subscribe_market_data(self, commodity_id: str, callback: Callable) -> bool:
        """Register a callback for simulated market data.

        Use ``inject_tick`` to feed data to registered callbacks.

        Args:
            commodity_id: Commodity identifier.
            callback: Callback for market data events.

        Returns:
            Always True.
        """
        if commodity_id not in self._market_data_callbacks:
            self._market_data_callbacks[commodity_id] = []
        self._market_data_callbacks[commodity_id].append(callback)
        return True

    def convert_enum(self, domain_enum: Any) -> Any:
        """Pass-through enum conversion (no exchange-specific mapping needed).

        Args:
            domain_enum: Domain enumeration value.

        Returns:
            The same enum value unchanged.
        """
        return domain_enum

    def parse_decimal(self, value: float) -> Any:
        """Pass-through decimal conversion.

        Args:
            value: Float value.

        Returns:
            The same float value unchanged.
        """
        return value

    def get_client(self) -> Any:
        """Return self as the simulator client.

        Returns:
            The simulator adapter itself.
        """
        return self

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for simulated events.

        Args:
            event_type: Event type identifier.
            callback: Callback function.
        """
        if event_type not in self._market_data_callbacks:
            self._market_data_callbacks[event_type] = []
        self._market_data_callbacks[event_type].append(callback)

    # ------------------------------------------------------------------ #
    #  Simulator-specific helpers                                         #
    # ------------------------------------------------------------------ #

    def inject_tick(self, commodity_id: str, price: float) -> None:
        """Inject a simulated tick into registered callbacks.

        Args:
            commodity_id: Commodity identifier.
            price: Simulated price.
        """
        callbacks = self._market_data_callbacks.get(commodity_id, [])
        for cb in callbacks:
            cb(commodity_id, "", "", str(price), "0", "0", "1", "1", None, None)

    def add_position(self, position: PositionDto) -> None:
        """Add a simulated position for testing.

        Args:
            position: Position DTO to add.
        """
        self._positions.append(position)

    def clear(self) -> None:
        """Reset all simulator state."""
        self._orders.clear()
        self._positions.clear()
        self._market_data_callbacks.clear()

    @property
    def orders(self) -> List[dict]:
        """Get all recorded orders."""
        return list(self._orders)

    @property
    def is_connected(self) -> bool:
        """Check if simulator is connected."""
        return self._connected
