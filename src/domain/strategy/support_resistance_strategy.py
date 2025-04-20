"""Support Resistance Strategy Implementation.

This strategy monitors price movement and triggers signals based on support and resistance levels,
communicating signals via ZeroMQ.
"""

from src.infrastructure.messaging import ZmqPusher, serialize  # Import ZMQ Pusher and serializer
from src.infrastructure.events.tick import TickEvent
from src.infrastructure.events.trading_signal import TradingSignal
from src.domain.value_objects import OrderOperation
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.domain.entities.condition import Condition
from typing import Optional


class SupportResistanceStrategy:
    """Strategy that uses support and resistance levels to generate trading signals via ZMQ."""

    def __init__(
        self,
        condition_repository: ConditionRepositoryInterface,
        signal_pusher: ZmqPusher,  # Inject ZmqPusher
        logger: LoggerInterface = None,
    ):
        """Initialize the support and resistance strategy.

        Args:
            # event_dispatcher: The event dispatcher to subscribe to for tick events and publish signals
            condition_repository: Repository for accessing trading conditions
            signal_pusher: The ZeroMQ pusher for sending trading signals.
            logger: Optional logger for recording strategy events
        """
        # self.event_dispatcher = event_dispatcher
        self.condition_repository = condition_repository
        self.signal_pusher = signal_pusher  # Store the pusher
        self.logger = logger

        # Remove subscription to tick events
        # event_dispatcher.subscribe_event_type("TICK", self.on_tick)

    # Rename on_tick to process_tick_event, as it's no longer an event handler callback
    def process_tick_event(self, tick_event: TickEvent):
        """Process a TickEvent received (e.g., via ZMQ) and generate trading signals if conditions are met.

        Args:
            tick_event: The tick event containing current price information
        """
        # Extract current price from the tick event
        price = int(tick_event.tick.match_price)
        # print(f"Price: {price}")

        # Get all active conditions (Consider optimizing this for HFT)
        conditions = self.condition_repository.get_all()

        # Process each condition - iterate over a copy of the values
        for condition in list(conditions.values()):
            self._process_condition(condition, price, tick_event)

            # Update the condition in the repository (Consider making this async/batched)
            # Check if condition still exists before updating (it might have been deleted in _process_condition)
            # We can check if it's exited OR try/except the update
            if not condition.is_exited:
                try:
                    self.condition_repository.update(condition)
                except KeyError:  # Or a more specific "NotFound" error if your repo has one
                    self._log(
                        f"Condition {condition.condition_id} already deleted, skipping update.",
                        level="warning",
                    )

    def _process_condition(self, condition: Condition, price: int, tick_event: TickEvent):
        """Process a single condition against the current price.

        Args:
            condition: The trading condition to evaluate
            price: The current price
            tick_event: The original tick event
        """
        # Handle trigger detection
        if not condition.is_trigger:
            if self._should_trigger(condition, price):
                self._log(f"Condition {condition.condition_id} triggered at price {price}")
                condition.is_trigger = True

        # Handle order execution
        elif not condition.is_ordered:
            if self._should_order(condition, price):
                self._log(f"Condition {condition.condition_id} ordering at price {price}")
                # Use the injected pusher to send the signal
                self._send_trading_signal(condition.action, tick_event)
                condition.is_ordered = True

        # Handle exit conditions
        elif not condition.is_exited:
            exit_reason = self._should_exit(condition, price)
            if exit_reason:
                self._log(f"Condition {condition.condition_id} exiting: {exit_reason}")

                # Determine the exit action (opposite of entry)
                exit_action = (
                    OrderOperation.SELL
                    if condition.action == OrderOperation.BUY
                    else OrderOperation.BUY
                )
                # Use the injected pusher to send the exit signal
                self._send_trading_signal(exit_action, tick_event)

                condition.is_exited = True
                # Delete the condition AFTER sending the signal
                self.condition_repository.delete(condition.condition_id)

        # Handle trailing conditions (only if not exited)
        if condition.is_following and not condition.is_ordered and not condition.is_exited:
            self._update_trailing_condition(condition, price)

    def _should_trigger(self, condition: Condition, price: int) -> bool:
        """Check if a condition should be triggered.

        Args:
            condition: The condition to check
            price: Current price

        Returns:
            bool: True if condition should be triggered
        """
        if condition.action == OrderOperation.BUY:
            # For buy, trigger when price falls below support level
            return price <= condition.trigger_price
        else:  # OrderOperation.SELL
            # For sell, trigger when price rises above resistance level
            return price >= condition.trigger_price

    def _should_order(self, condition: Condition, price: int) -> bool:
        """Check if an order should be placed.

        Args:
            condition: The triggered condition
            price: Current price

        Returns:
            bool: True if an order should be placed
        """
        if condition.action == OrderOperation.BUY:
            # For buy, order when price rises to entry point after triggering
            return price >= condition.order_price
        else:  # OrderOperation.SELL
            # For sell, order when price falls to entry point after triggering
            return price <= condition.order_price

    def _should_exit(
        self, condition: Condition, price: int
    ) -> Optional[str]:  # Return type changed Optional[str]
        """Check if position should be exited.

        Args:
            condition: The active condition with an open position
            price: Current price

        Returns:
            str: Reason for exit or None if no exit needed
        """
        if condition.action == OrderOperation.BUY:
            # For long positions
            if price >= condition.take_profit_price:
                return "Take profit"
            if price <= condition.stop_loss_price:
                return "Stop loss"
        else:  # OrderOperation.SELL
            # For short positions
            if price <= condition.take_profit_price:
                return "Take profit"
            if price >= condition.stop_loss_price:
                return "Stop loss"

        return None

    def _update_trailing_condition(self, condition: Condition, price: int):
        """Update trailing condition prices.

        Args:
            condition: The condition with trailing enabled
            price: Current price
        """
        # Ensure turning_point is positive
        turning_point_abs = abs(condition.turning_point or 0)
        if turning_point_abs == 0:
            if self.logger:
                self.logger.log_warning(
                    f"Trailing condition {condition.condition_id} has zero turning point. Trailing disabled."
                )
            return

        if condition.action == OrderOperation.BUY:
            # For buy, update trigger and order prices as price moves lower
            if price <= condition.trigger_price:
                new_order_price = price + turning_point_abs
                self._log(
                    f"Updating trailing buy condition {condition.condition_id} to trigger price {price}, order price {new_order_price}"
                )
                condition.trigger_price = price
                condition.order_price = new_order_price
        else:  # OrderOperation.SELL
            # For sell, update trigger and order prices as price moves higher
            if price >= condition.trigger_price:
                new_order_price = price - turning_point_abs
                self._log(
                    f"Updating trailing sell condition {condition.condition_id} to trigger price {price}, order price {new_order_price}"
                )
                condition.trigger_price = price
                condition.order_price = new_order_price

    def _send_trading_signal(self, action: OrderOperation, tick_event: TickEvent):
        """Send a trading signal via the injected ZMQ Pusher.

        Args:
            action: Buy or sell action
            tick_event: The originating tick event (used for commodity_id and timestamp)
        """
        signal = TradingSignal(
            tick_event.when,  # Use timestamp from the original event
            action,
            tick_event.tick.commodity_id,
        )
        try:
            # Serialize the signal
            serialized_signal = serialize(signal)
            # Send using the pusher
            self.signal_pusher.send(serialized_signal)
            self._log(f"Sent trading signal via ZMQ: {action.name} {tick_event.tick.commodity_id}")
        except Exception as e:
            self._log(f"Failed to send trading signal via ZMQ: {e}", level="error")

        # Remove event dispatcher publishing
        # self.event_dispatcher.publish_event("TRADING_SIGNAL", signal)

    def _log(self, message: str, level: str = "info"):
        """Log a message if logger is available.

        Args:
            message: The message to log
            level: Log level ('info', 'error', 'warning', etc.)
        """
        if self.logger:
            log_func = getattr(self.logger, f"log_{level}", self.logger.log_info)
            log_func(message)
        else:
            # Basic print fallback if no logger
            print(f"[{level.upper()}] {message}")

    # Add a close method for the pusher if needed
    def close(self):
        if self.logger:
            self.logger.log_info("Closing Strategy resources (ZMQ pusher).")
        # self.signal_pusher.close() # Pusher might be shared, close at higher level
        pass
