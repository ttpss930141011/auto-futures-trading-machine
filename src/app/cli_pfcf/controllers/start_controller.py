"""StartController for centralizing application flow with proper SOLID principles.

This controller handles the application startup, verification of prerequisites,
and initialization of all required components following Clean Architecture principles.
"""
import asyncio
from typing import Dict

from src.domain.value_objects import OrderOperation
from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.events.dispatcher import RealtimeDispatcher
from src.infrastructure.pfcf_client.tick_producer import TickProducer
from src.domain.strategy.support_resistance_strategy import SupportResistanceStrategy
from src.domain.order.order_executor import OrderExecutor
from src.infrastructure.event_sources.trading_signal import TradingSignalSource
from src.interactor.errors.error_classes import LoginFailedException, NotFountItemException
from src.interactor.use_cases.start_application import StartApplicationUseCase
from src.infrastructure.services.status_checker import StatusChecker


class StartController(CliMemoryControllerInterface):
    """Controller for starting the application with all prerequisites checks."""
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository
        self.status_checker = StatusChecker(service_container)
        
        # Create the event dispatcher with logger
        self.event_dispatcher = RealtimeDispatcher(logger=service_container.logger)
        
        # Initialize component references
        self.tick_producer = None
        self.trading_signal_source = None
        self.strategy = None
        self.order_executor = None
    
    def execute(self) -> None:
        """Execute the start sequence with validation of prerequisites."""
        try:
            # Check if user is logged in
            if not self.session_repository.is_user_logged_in():
                self.logger.log_info("User not login")
                print("Please login first (option 1)")
                return
                
            # Create use case
            start_app_use_case = StartApplicationUseCase(
                logger=self.logger,
                status_checker=self.status_checker
            )
            
            # Execute the use case
            status_summary = start_app_use_case.execute()
            
            # Display status to user
            self._display_status_summary(status_summary)
            
            # Check if we can proceed
            if not self._can_proceed(status_summary):
                self.logger.log_warning("Prerequisites not met. Please complete the setup before starting.")
                return
            
            # Initialize and start the application components
            self._initialize_components()
            self._start_application()
            
            self.logger.log_info("Application started successfully. Trading system is now active.")
            
        except Exception as e:
            self.logger.log_error(f"Failed to start application: {str(e)}")
    
    def _display_status_summary(self, status_summary: Dict[str, bool]) -> None:
        """Display status summary to the user."""
        print("\n=== System Status ===")
        print(f"User logged in: {'✓' if status_summary['logged_in'] else '✗'}")
        print(f"Item registered: {'✓' if status_summary['item_registered'] else '✗'}")
        print(f"Order account selected: {'✓' if status_summary['order_account_selected'] else '✗'}")
        print(f"Trading conditions defined: {'✓' if status_summary['has_conditions'] else '✗'}")
        print("=====================\n")
    
    def _can_proceed(self, status_summary: Dict[str, bool]) -> bool:
        """Check if all prerequisites are met to start the application."""
        return all(status_summary.values())
        
    def _initialize_components(self) -> None:
        """Initialize all components needed for trading."""
        # Create trading signal source
        self.trading_signal_source = TradingSignalSource(
            self.event_dispatcher,
            producer=None
        )
        
        # Initialize tick producer with event buffering
        self.tick_producer = TickProducer(
            self.event_dispatcher,
            self.logger,
            buffer_size=1000  # Buffer up to 1000 tick events
        )
        
        # Initialize strategy
        self.strategy = SupportResistanceStrategy(
            self.event_dispatcher,
            self.service_container.condition_repository,
            self.logger
        )
        
        # Initialize order executor
        self.order_executor = OrderExecutor(
            self.event_dispatcher,
            self.service_container.send_market_order_use_case,
            self.session_repository,
            self.logger
        )
        
        # Connect PFCF API callbacks to tick producer
        self._connect_api_callbacks()
    
    def _connect_api_callbacks(self) -> None:
        """Connect API callbacks to the tick producer."""
        # Get the API client from the configuration
        exchange_api = self.config.EXCHANGE_API
        
        # Connect the tick data callback
        def on_tick_data_trade(commodity_id, info_time, match_time, match_price, 
                            match_buy_cnt, match_sell_cnt, match_quantity, match_total_qty,
                            match_price_data, match_qty_data):
            self.tick_producer.handle_tick_data(
                commodity_id, info_time, match_time, match_price, 
                match_buy_cnt, match_sell_cnt, match_quantity, match_total_qty,
                match_price_data, match_qty_data
            )
        
        # Register the callback
        exchange_api.client.DQuoteLib.OnTickDataTrade += on_tick_data_trade
        
        # Register the item to listen for market data
        item_code = self.session_repository.get_item_code()
        if item_code:
            self.logger.log_info(f"Registering item {item_code} for market data")
            exchange_api.client.DQuoteLib.RegItem(item_code)
        else:
            self.logger.log_error("No item code found in session")
            
    def _start_application(self) -> None:
        """Start the event dispatcher and trading workflow."""
        # Import datetime here to avoid circular imports
        import datetime
        
        # Create a background task to run the event dispatcher
        dispatcher_task = asyncio.create_task(self.event_dispatcher.run())
        
        # Schedule to log buffer statistics periodically
        self.event_dispatcher.schedule(
            datetime.datetime.now() + datetime.timedelta(minutes=1),
            self._log_buffer_statistics
        )
        
        # Log that the system is now monitoring the market
        self.logger.log_info(f"Now monitoring market data for {self.session_repository.get_item_code()}")
        self.logger.log_info("Trading conditions are active")
        
        # Display active conditions
        self._display_active_conditions()
        
        # Keep the controller running until user exits
        print("\nTrading system is now active and monitoring the market.")
        print("Press Ctrl+C to stop or return to the main menu.")
        
    def _log_buffer_statistics(self) -> None:
        """Log statistics about event buffers periodically."""
        # Import datetime here to avoid circular imports
        import datetime
        
        # This is scheduled to run periodically
        if hasattr(self.tick_producer, 'tick_buffer'):
            buffer_size = self.tick_producer.tick_buffer.size()
            self.logger.log_info(f"Tick buffer contains {buffer_size} events")
        
        # Reschedule for the next minute
        self.event_dispatcher.schedule(
            datetime.datetime.now() + datetime.timedelta(minutes=1),
            self._log_buffer_statistics
        )
        
    def _display_active_conditions(self) -> None:
        """Display all active trading conditions."""
        conditions = self.service_container.condition_repository.get_all()
        
        if not conditions:
            print("No active trading conditions found.")
            return
            
        print("\n=== Active Trading Conditions ===")
        for condition_id, condition in conditions.items():
            direction = "BUY" if condition.action == OrderOperation.BUY else "SELL"
            print(f"ID: {condition_id} | Direction: {direction}")
            print(f"  Trigger Price: {condition.trigger_price}")
            print(f"  Order Price: {condition.order_price}")
            print(f"  Take Profit: {condition.take_profit_price}")
            print(f"  Stop Loss: {condition.stop_loss_price}")
            print(f"  Status: {'Triggered' if condition.is_trigger else 'Waiting'}")
            print("----------------------------")
        print("================================\n")