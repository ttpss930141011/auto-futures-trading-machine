"""ZMQ Gateway Controller for initializing market data bridge between API and trading components.

This controller initializes the ZeroMQ infrastructure to bridge market data from the exchange API
to other components of the trading system. It sets up the necessary sockets for publishing tick data
and receiving trading signals, without implementing the trading logic itself.
"""

from typing import Dict, Optional
import zmq
import socket
import asyncio
import signal
import time
from contextlib import closing

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.messaging import (
    ZmqPublisher,
    ZmqPuller,
)
from src.infrastructure.pfcf_client.tick_producer import TickProducer
from src.interactor.use_cases.application_startup_status import ApplicationStartupStatusUseCase
from src.infrastructure.services.status_checker import StatusChecker


class GatewayController(CliMemoryControllerInterface):
    """Controller for initializing ZeroMQ market data gateway infrastructure."""

    def __init__(self, service_container: ServiceContainer, is_threaded_mode: bool = False):
        """Initialize the gateway controller.

        Args:
            service_container: Container with all services and dependencies
            is_threaded_mode: Whether this controller is running in a thread
        """
        self.service_container = service_container
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository
        self.status_checker = StatusChecker(service_container)
        self.is_threaded_mode = is_threaded_mode

        # Create a shared ZMQ context
        self.zmq_context = zmq.Context.instance()

        # Initialize component references
        self.tick_publisher: Optional[ZmqPublisher] = None
        self.signal_puller: Optional[ZmqPuller] = None  # For receiving signals from Strategy
        self.tick_producer: Optional[TickProducer] = None

        # Flag to control the running state
        self.running = False

    def execute(self) -> None:
        """Execute the gateway initialization and run the event processing loop.

        This method initializes the ZeroMQ sockets for publishing market data and
        receiving trading signals, then enters a loop to process API events.
        """
        try:
            # Check if user is logged in
            if not self.session_repository.is_user_logged_in():
                self.logger.log_info("User not login")
                print("Please login first (option 1)")
                return

            # Create and execute use case for status checks
            start_app_use_case = ApplicationStartupStatusUseCase(
                logger=self.logger, status_checker=self.status_checker
            )

            status_summary = start_app_use_case.execute()

            # Display status to user
            self._display_status_summary(status_summary)

            # Check if we can proceed
            if not self._can_proceed(status_summary):
                self.logger.log_warning(
                    "Prerequisites not met. Please complete the setup before starting."
                )
                return

            # Check port availability before initializing components
            port_status = self._check_port_availability()
            if not all(port_status.values()):
                self.logger.log_error("Required ports are not available")
                print("\nERROR: One or more required ports are in use by other applications:")
                for port, available in port_status.items():
                    if not available:
                        print(f"- Port {port} is already in use")
                print("\nSolutions:")
                print("- Close other instances of this application")
                print("- Close any other applications using these ports")
                print("- Change the port configuration (requires code modification)")
                return

            # Initialize ZMQ sockets and gateway components
            try:
                self._initialize_components()
            except Exception as e:
                self.logger.log_error(f"Component initialization failed: {str(e)}")
                print(f"\nERROR: Failed to initialize components: {str(e)}")
                return

            # Verify successful initialization before proceeding
            if (
                not self.tick_publisher
                or not hasattr(self.tick_publisher, "_is_initialized")
                or not self.tick_publisher._is_initialized
            ):
                self.logger.log_error("Critical component initialization failed.")
                print("\nERROR: Critical component initialization failed. Check logs for details.")
                return

            self.logger.log_info("Gateway components initialized successfully with ZeroMQ sockets.")
            self.logger.log_info(
                f" - Tick Publisher listening on: {self.config.ZMQ_TICK_PUB_ADDRESS}"
            )
            self.logger.log_info(
                f" - Signal Puller listening on: {self.config.ZMQ_SIGNAL_PULL_ADDRESS}"
            )

            print("\n=== ZeroMQ Market Data Gateway Initialized ===")
            print(f"Publishing ticks on: {self.config.ZMQ_TICK_SUB_CONNECT_ADDRESS}")
            print(f"Receiving signals on: {self.config.ZMQ_SIGNAL_PULL_ADDRESS}")
            print("\nTo complete the trading system, you need to:")
            print("1. Run the strategy process (run_strategy.py)")
            print("2. Run the order executor process (run_order_executor.py)")

            if not self.is_threaded_mode:
                print("\nThe gateway is now running. Press Ctrl+C to stop.")

            # Connect API callbacks
            self._connect_api_callbacks()

            # Set running flag
            self.running = True

            # Start the main processing loop to keep the gateway alive
            self._run_event_loop()

        except Exception as e:
            self.logger.log_error(f"Failed to start ZMQ gateway: {str(e)}")
            print(f"\nERROR: Gateway start failed: {str(e)}")
        finally:
            if self.running:
                self._cleanup_zmq()

    def _run_event_loop(self):
        """Run the event processing loop to keep the gateway alive.

        This method implements a simple loop that keeps the gateway process running
        until interrupted by the user or an error occurs.
        """
        try:
            # Register signal handlers for graceful shutdown - ONLY in main thread mode
            if not self.is_threaded_mode:
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)

            self.logger.log_info("Gateway event loop started")

            # Simple loop that keeps the process alive
            # In a real application, this might involve more active processing
            while self.running:
                # Sleep to reduce CPU usage
                time.sleep(0.1)

                # Here you could add periodic tasks if needed:
                # - Health checks
                # - Status updates
                # - Monitoring

        except KeyboardInterrupt:
            self.logger.log_info("Gateway shutdown initiated by keyboard interrupt")
            print("\nGateway shutdown initiated")
        except Exception as e:
            self.logger.log_error(f"Gateway event loop error: {str(e)}")
            print(f"\nERROR: Gateway event loop error: {str(e)}")
        finally:
            self.running = False
            self.logger.log_info("Gateway event loop terminated")

    def _signal_handler(self, sig, frame):
        """Handle termination signals for graceful shutdown.

        Args:
            sig: Signal number
            frame: Current stack frame
        """
        self.logger.log_info(f"Received signal {sig}, initiating gateway shutdown")
        self.running = False

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
        """Check if all prerequisites are met to start the gateway.

        Args:
            status_summary: Dictionary with status check results

        Returns:
            True if all checks passed, False otherwise
        """
        return all(status_summary.values())

    def _initialize_components(self) -> None:
        """Initialize ZeroMQ sockets and components needed for the market data gateway."""
        self.logger.log_info("Initializing ZeroMQ components for gateway...")

        try:
            # Initialize ZMQ sockets with error checking
            self.tick_publisher = ZmqPublisher(
                self.config.ZMQ_TICK_PUB_ADDRESS, self.logger, self.zmq_context
            )

            # Verify publisher initialization
            if (
                not hasattr(self.tick_publisher, "_is_initialized")
                or not self.tick_publisher._is_initialized
            ):
                self.logger.log_error(
                    "Tick Publisher initialization failed. Check network and port availability."
                )
                print("\nERROR: Failed to initialize ZMQ Publisher. Check logs for details.")
                print(
                    f"- Ensure port {self.config.ZMQ_TICK_PORT} is available and not blocked by firewall"
                )
                print("- Verify no other instances are running using the same ports")
                return

            self.signal_puller = ZmqPuller(
                self.config.ZMQ_SIGNAL_PULL_ADDRESS, self.logger, self.zmq_context
            )

            # Initialize TickProducer with verified publisher
            self.tick_producer = TickProducer(
                tick_publisher=self.tick_publisher,
                logger=self.logger,
            )

            # Verification message for successful initialization
            self.logger.log_info("ZeroMQ gateway components initialized successfully.")

        except Exception as e:
            self.logger.log_error(f"Failed to initialize ZeroMQ gateway components: {str(e)}")
            print(f"\nERROR: Gateway component initialization failed: {str(e)}")
            # Ensure cleanup happens in case of partial initialization
            self._cleanup_zmq()
            raise

    def _connect_api_callbacks(self) -> None:
        """Connect API callbacks to the tick producer."""
        if not self.tick_producer:
            self.logger.log_error("TickProducer not initialized. Cannot connect API callbacks.")
            return

        # Connect the tick data callback
        def on_tick_data_trade(
            commodity_id,
            info_time,
            match_time,
            match_price,
            match_buy_cnt,
            match_sell_cnt,
            match_quantity,
            match_total_qty,
            match_price_data,
            match_qty_data,
        ):
            # Ensure tick_producer exists before calling method
            if self.tick_producer:
                self.tick_producer.handle_tick_data(
                    commodity_id,
                    info_time,
                    match_time,
                    match_price,
                    match_buy_cnt,
                    match_sell_cnt,
                    match_quantity,
                    match_total_qty,
                    match_price_data,
                    match_qty_data,
                )
            else:
                # This should ideally not happen if initialization is correct
                print("ERROR: TickProducer called before initialization in API callback!")

        # Register the callback (Assuming EXCHANGE_CLIENT is available)
        try:
            if (
                self.config
                and hasattr(self.config, "EXCHANGE_CLIENT")
                and self.config.EXCHANGE_CLIENT
            ):
                self.config.EXCHANGE_CLIENT.DQuoteLib.OnTickDataTrade += on_tick_data_trade
                self.logger.log_info("Successfully registered OnTickDataTrade callback.")

                # Register the item to listen for market data
                item_code = self.session_repository.get_item_code()
                if item_code:
                    self.logger.log_info(f"Registering item {item_code} for market data via API")
                    self.config.EXCHANGE_CLIENT.DQuoteLib.RegItem(item_code)
                else:
                    self.logger.log_error(
                        "No item code found in session. Cannot register for market data."
                    )
            else:
                self.logger.log_error(
                    "Exchange client not configured or available. Cannot register API callback."
                )
        except AttributeError as e:
            self.logger.log_error(
                f"Error accessing EXCHANGE_CLIENT or DQuoteLib: {e}. API callbacks not registered."
            )
        except Exception as e:  # Catch other potential errors during registration
            self.logger.log_error(f"Unexpected error registering API callback: {e}")

    def _cleanup_zmq(self):
        """Close ZMQ sockets and terminate context gracefully."""
        self.logger.log_info("Cleaning up Gateway ZMQ resources...")

        # Close sockets managed by this controller
        if hasattr(self, "tick_publisher") and self.tick_publisher:
            try:
                self.tick_publisher.close()
                self.logger.log_info("Tick Publisher closed successfully.")
            except Exception as e:
                self.logger.log_error(f"Error closing Tick Publisher: {str(e)}")

        if hasattr(self, "signal_puller") and self.signal_puller:
            try:
                self.signal_puller.close()
                self.logger.log_info("Signal Puller closed successfully.")
            except Exception as e:
                self.logger.log_error(f"Error closing Signal Puller: {str(e)}")

        if hasattr(self, "tick_producer") and self.tick_producer:
            try:
                self.tick_producer.close()
                self.logger.log_info("Tick Producer closed successfully.")
            except Exception as e:
                self.logger.log_error(f"Error closing Tick Producer: {str(e)}")

        # Terminate the context last
        if hasattr(self, "zmq_context") and self.zmq_context and not self.zmq_context.closed:
            try:
                self.zmq_context.term()
                self.logger.log_info("ZMQ context terminated.")
            except Exception as e:
                self.logger.log_error(f"Error terminating ZMQ context: {str(e)}")

    def _check_port_availability(self) -> Dict[str, bool]:
        """Check if the required ports are available.

        Returns:
            Dict[str, bool]: Dictionary with port numbers as keys and availability as values
        """
        ports_to_check = {
            self.config.ZMQ_TICK_PORT: "Publisher port",
            self.config.ZMQ_SIGNAL_PORT: "Signal Puller port",
        }
        results = {}

        for port, description in ports_to_check.items():
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                try:
                    sock.bind(("127.0.0.1", port))
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.logger.log_info(f"Port {port} ({description}) is available")
                    results[port] = True
                except socket.error:
                    self.logger.log_error(f"Port {port} ({description}) is already in use")
                    results[port] = False

        return results
