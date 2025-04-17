"""Support Resistance Strategy Implementation.

This strategy monitors price movement and triggers signals based on support and resistance levels.
"""
from src.infrastructure.events.dispatcher import RealtimeDispatcher
from src.infrastructure.events.tick import TickEvent
from src.infrastructure.event_sources.trading_signal import TradingSignal
from src.domain.value_objects import OrderOperation
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.domain.entities.condition import Condition


class SupportResistanceStrategy:
    """Strategy that uses support and resistance levels to generate trading signals."""
    
    def __init__(self, 
                 event_dispatcher: RealtimeDispatcher, 
                 condition_repository: ConditionRepositoryInterface,
                 logger: LoggerInterface = None):
        """Initialize the support and resistance strategy.
        
        Args:
            event_dispatcher: The event dispatcher to subscribe to for tick events and publish signals
            condition_repository: Repository for accessing trading conditions
            logger: Optional logger for recording strategy events
        """
        self.event_dispatcher = event_dispatcher
        self.condition_repository = condition_repository
        self.logger = logger
        
        # Subscribe to tick events
        event_dispatcher.subscribe_event_type("TICK", self.on_tick)
    
    def on_tick(self, tick_event: TickEvent):
        """Process a tick event and generate trading signals if conditions are met.
        
        Args:
            tick_event: The tick event containing current price information
        """
        # Extract current price from the tick event
        price = int(tick_event.tick.match_price)
        print(f"Price: {price}")
        
        # Get all active conditions
        conditions = self.condition_repository.get_all()
        
        # Process each condition
        for condition in conditions.values():
            self._process_condition(condition, price, tick_event)
            
            # Update the condition in the repository
            self.condition_repository.update(condition)
    
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
                self._send_trading_signal(condition.action, tick_event)
                condition.is_ordered = True
        
        # Handle exit conditions
        elif not condition.is_exited:
            exit_reason = self._should_exit(condition, price)
            if exit_reason:
                self._log(f"Condition {condition.condition_id} exiting: {exit_reason}")
                
                # Determine the exit action (opposite of entry)
                exit_action = OrderOperation.SELL if condition.action == OrderOperation.BUY else OrderOperation.BUY
                self._send_trading_signal(exit_action, tick_event)
                
                condition.is_exited = True
                self.condition_repository.delete(condition.condition_id)
        
        # Handle trailing conditions
        if condition.is_following and not condition.is_ordered:
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
    
    def _should_exit(self, condition: Condition, price: int) -> str:
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
        if condition.action == OrderOperation.BUY:
            # For buy, update trigger and order prices as price moves lower
            if price <= condition.trigger_price:
                self._log(f"Updating trailing buy condition {condition.condition_id} to price {price}")
                condition.trigger_price = price
                condition.order_price = price + condition.turning_point
        else:  # OrderOperation.SELL
            # For sell, update trigger and order prices as price moves higher
            if price >= condition.trigger_price:
                self._log(f"Updating trailing sell condition {condition.condition_id} to price {price}")
                condition.trigger_price = price
                condition.order_price = price - condition.turning_point
    
    def _send_trading_signal(self, action: OrderOperation, tick_event: TickEvent):
        """Send a trading signal through the event dispatcher.
        
        Args:
            action: Buy or sell action
            tick_event: The originating tick event
        """
        signal = TradingSignal(
            tick_event.when,
            action,
            tick_event.tick.commodity_id
        )
        self.event_dispatcher.publish_event("TRADING_SIGNAL", signal)
    
    def _log(self, message: str):
        """Log a message if logger is available.
        
        Args:
            message: The message to log
        """
        if self.logger:
            self.logger.log_info(message)