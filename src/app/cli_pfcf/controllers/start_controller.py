"""StartController for initializing components for a distributed trading system using ZeroMQ.

This controller handles the application startup, verification of prerequisites,
and initialization of components that communicate via ZeroMQ, suitable for running in separate processes.
"""
import asyncio # Keep for potential future async operations, but remove event loop run
import datetime
import zmq # Import zmq for context management
from typing import Dict, Optional

from src.domain.value_objects import OrderOperation
from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.messaging import ZmqPublisher, ZmqPusher, ZmqPuller, serialize, deserialize # Import ZMQ components
from src.infrastructure.adapters.tick_producer import TickProducer
from src.domain.strategy.support_resistance_strategy import SupportResistanceStrategy
from src.domain.order.order_executor import OrderExecutor
from src.interactor.errors.error_classes import LoginFailedException, NotFountItemException
from src.interactor.use_cases.start_application import StartApplicationUseCase
from src.infrastructure.services.status_checker import StatusChecker

# Define ZMQ addresses (Consider making these configurable)
ZMQ_TICK_PUB_ADDRESS = "tcp://*:5555"
ZMQ_SIGNAL_PULL_ADDRESS = "tcp://*:5556"
# Addresses for clients (Strategy, OrderExecutor) to connect to
ZMQ_TICK_SUB_CONNECT_ADDRESS = "tcp://localhost:5555"
ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS = "tcp://localhost:5556"


class StartController(CliMemoryControllerInterface):
    """Controller for initializing components for ZeroMQ-based trading system."""
    
    def __init__(self, service_container: ServiceContainer):
        """Initialize the start controller.
        
        Args:
            service_container: Container with all services and dependencies
        """
        self.service_container = service_container
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository
        self.status_checker = StatusChecker(service_container)
        
        
        # Create a shared ZMQ context
        self.zmq_context = zmq.Context.instance()

        # Initialize component references
        self.tick_publisher: Optional[ZmqPublisher] = None
        self.signal_puller: Optional[ZmqPuller] = None # For OrderExecutor process
        self.signal_pusher: Optional[ZmqPusher] = None   # For Strategy process
        self.tick_producer: Optional[TickProducer] = None
        self.strategy: Optional[SupportResistanceStrategy] = None
        self.order_executor: Optional[OrderExecutor] = None
    
    def execute(self) -> None:
        """Execute the initialization sequence.
        
        This method now focuses on checking prerequisites and initializing components.
        It does NOT start a persistent event loop here. Components are expected to be run
        in separate processes/scripts.
        """
        try:
            # Check if user is logged in
            if not self.session_repository.is_user_logged_in():
                self.logger.log_info("User not login")
                print("Please login first (option 1)")
                return
                
            # Create and execute use case for status checks
            start_app_use_case = StartApplicationUseCase(
                logger=self.logger,
                status_checker=self.status_checker
            )
            
            status_summary = start_app_use_case.execute()
            
            # Display status to user
            self._display_status_summary(status_summary)
            
            # Check if we can proceed
            if not self._can_proceed(status_summary):
                self.logger.log_warning("Prerequisites not met. Please complete the setup before starting.")
                return
            
            # Initialize ZMQ sockets and application components
            self._initialize_components()
            
            # Remove the old application start logic
            # self._start_application() 
            
            self.logger.log_info("Application components initialized successfully with ZeroMQ sockets.")
            self.logger.log_info(f" - Tick Publisher listening on: {ZMQ_TICK_PUB_ADDRESS}")
            self.logger.log_info(f" - Signal Puller listening on: {ZMQ_SIGNAL_PULL_ADDRESS}")
            print("\nComponents initialized. Run separate processes for Strategy and Order Execution.")
            print(f"Strategy should connect SUB to {ZMQ_TICK_SUB_CONNECT_ADDRESS} and PUSH to {ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS}")
            print(f"OrderExecutor should connect PULL to {ZMQ_SIGNAL_PULL_ADDRESS}") # Puller binds, Pusher connects

            # Display active conditions as before
            self._display_active_conditions()
            
            # Connect API callbacks (This part stays, assuming this controller runs in the gateway process)
            self._connect_api_callbacks()

            # The controller's job here is done after initialization and connecting callbacks.
            # The actual running happens in the API event loop or separate processes.
            print("\nGateway initialized. Listening for API callbacks and publishing ticks...")
            print("Press Ctrl+C to stop the gateway/callback listener.")
            # Keep the main thread alive if this process needs to run indefinitely for callbacks
            # In a real scenario, the PFCF client might manage its own loop.
            # For simplicity here, we might just wait indefinitely or rely on the calling script.
            # asyncio.get_event_loop().run_forever() # Example if an event loop is still needed for API

        except Exception as e:
            self.logger.log_error(f"Failed to initialize application components: {str(e)}")
        finally:
            # Ensure ZMQ context is terminated on exit
            self._cleanup_zmq()

    def _display_status_summary(self, status_summary: Dict[str, bool]) -> None:
        """Display status summary to the user.
        
        Args:
            status_summary: Dictionary with status check results
        """
        print("\n=== System Status ===")
        print(f"User logged in: {'✓' if status_summary['logged_in'] else '✗'}")
        print(f"Item registered: {'✓' if status_summary['item_registered'] else '✗'}")
        print(f"Order account selected: {'✓' if status_summary['order_account_selected'] else '✗'}")
        print(f"Trading conditions defined: {'✓' if status_summary['has_conditions'] else '✗'}")
        print("=====================\n")
    
    def _can_proceed(self, status_summary: Dict[str, bool]) -> bool:
        """Check if all prerequisites are met to start the application.
        
        Args:
            status_summary: Dictionary with status check results
            
        Returns:
            True if all checks passed, False otherwise
        """
        return all(status_summary.values())
    
    def _initialize_components(self) -> None:
        """Initialize ZMQ sockets and components needed for trading."""
        self.logger.log_info("Initializing ZeroMQ components...")

        # Initialize ZMQ sockets (Publisher binds, Puller binds)
        self.tick_publisher = ZmqPublisher(
            ZMQ_TICK_PUB_ADDRESS, self.logger, self.zmq_context
        )
        self.signal_puller = ZmqPuller(
            ZMQ_SIGNAL_PULL_ADDRESS, self.logger, self.zmq_context
        )
        # Pusher connects, so it would typically be initialized in the Strategy process
        # For demonstration if running monolithically, or for testing:
        # self.signal_pusher = ZmqPusher(
        #     ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS, self.logger, self.zmq_context
        # ) 

        # Initialize TickProducer (typically runs in Gateway process)
        self.tick_producer = TickProducer(
            tick_publisher=self.tick_publisher,
            logger=self.logger,
        )
        
        # Initialize Strategy (typically runs in separate Strategy process)
        # Requires a Pusher that connects to the Puller
        # For demonstration/testing, we might initialize it here, 
        # but it wouldn't receive ticks unless run alongside a subscriber.
        # strategy_signal_pusher = ZmqPusher(ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS, self.logger, self.zmq_context)
        # self.strategy = SupportResistanceStrategy(
        #     condition_repository=self.service_container.condition_repository,
        #     signal_pusher=strategy_signal_pusher, 
        #     logger=self.logger
        # )
        
        # Initialize Order Executor (typically runs in separate Executor process)
        # Uses the Puller initialized above
        self.order_executor = OrderExecutor(
            signal_puller=self.signal_puller,
            send_order_use_case=self.service_container.send_market_order_use_case,
            session_repository=self.session_repository,
            logger=self.logger
        )
        
        # Remove dispatcher connections and buffer scheduling
        # self._connect_api_callbacks() # Moved to execute() as it needs tick_producer
        # self._schedule_buffer_processing() # Removed
    
    def _connect_api_callbacks(self) -> None:
        """Connect API callbacks to the tick producer."""
        if not self.tick_producer:
             self.logger.log_error("TickProducer not initialized. Cannot connect API callbacks.")
             return
             
        # Connect the tick data callback
        def on_tick_data_trade(commodity_id, info_time, match_time, match_price, 
                            match_buy_cnt, match_sell_cnt, match_quantity, match_total_qty,
                            match_price_data, match_qty_data):
            # Ensure tick_producer exists before calling method
            if self.tick_producer: 
                self.tick_producer.handle_tick_data(
                    commodity_id, info_time, match_time, match_price, 
                    match_buy_cnt, match_sell_cnt, match_quantity, match_total_qty,
                    match_price_data, match_qty_data
                )
            else:
                 # This should ideally not happen if initialization is correct
                 print("ERROR: TickProducer called before initialization in API callback!") 
        
        # Register the callback (Assuming EXCHANGE_CLIENT is available)
        try:
            if self.config and hasattr(self.config, 'EXCHANGE_CLIENT') and self.config.EXCHANGE_CLIENT:
                 self.config.EXCHANGE_CLIENT.DQuoteLib.OnTickDataTrade += on_tick_data_trade
                 self.logger.log_info("Successfully registered OnTickDataTrade callback.")
                 
                 # Register the item to listen for market data
                 item_code = self.session_repository.get_item_code()
                 if item_code:
                     self.logger.log_info(f"Registering item {item_code} for market data via API")
                     self.config.EXCHANGE_CLIENT.DQuoteLib.RegItem(item_code)
                 else:
                     self.logger.log_error("No item code found in session. Cannot register for market data.")
            else:
                 self.logger.log_error("Exchange client not configured or available. Cannot register API callback.")
        except AttributeError as e:
             self.logger.log_error(f"Error accessing EXCHANGE_CLIENT or DQuoteLib: {e}. API callbacks not registered.")
        except Exception as e: # Catch other potential errors during registration
             self.logger.log_error(f"Unexpected error registering API callback: {e}")
    
    # Remove buffer processing methods
    # def _schedule_buffer_processing(self) -> None:
    #     ...
    # def _process_buffers(self) -> None:
    #     ...
    
    # Remove old start application method
    # def _start_application(self) -> None:
    #     ...

    def _display_active_conditions(self) -> None:
        """Display all active trading conditions."""
        conditions = self.service_container.condition_repository.get_all()
        
        if not conditions:
            print("No active trading conditions found.")
            return
            
        print("\n=== Active Trading Conditions (Loaded for reference) ===")
        for condition_id, condition in conditions.items():
            direction = "BUY" if condition.action == OrderOperation.BUY else "SELL"
            following = " (Trailing)" if condition.is_following else ""
            print(f"ID: {condition_id} | Direction: {direction}{following}")
            print(f"  Trigger Price: {condition.trigger_price}")
            print(f"  Order Price: {condition.order_price}")
            print(f"  Take Profit: {condition.take_profit_price}")
            print(f"  Stop Loss: {condition.stop_loss_price}")
            # Status here reflects initial state, runtime state is managed by strategy process
            # print(f"  Status: {'Triggered' if condition.is_trigger else 'Waiting'}") 
            print("----------------------------")
        print("=====================================================\n")
        
    def _cleanup_zmq(self): 
        """Close ZMQ sockets and terminate context gracefully."""
        self.logger.log_info("Cleaning up ZMQ resources...")
        # Close sockets managed by this controller (Publisher, Puller)
        if self.tick_publisher:
            self.tick_publisher.close()
        if self.signal_puller:
            self.signal_puller.close()
        # Close other components if initialized here for testing
        if self.tick_producer:
             self.tick_producer.close()
        if self.strategy:
             self.strategy.close()
        if self.order_executor:
             self.order_executor.close()
             
        # Terminate the context
        if self.zmq_context and not self.zmq_context.closed:
            self.zmq_context.term()
            self.logger.log_info("ZMQ context terminated.")