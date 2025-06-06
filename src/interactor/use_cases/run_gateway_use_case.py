"""Run Gateway Use Case.

This use case handles the complete lifecycle of running the gateway component,
including initialization, event loop, and graceful shutdown.
"""

import time
import signal
from typing import Dict, Optional, Callable, Tuple

from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.port_checker_service_interface import PortCheckerServiceInterface
from src.interactor.interfaces.services.gateway_initializer_service_interface import GatewayInitializerServiceInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


class RunGatewayUseCase:
    """Use case for running the gateway component with event loop."""

    def __init__(
        self,
        logger: LoggerInterface,
        port_checker_service: PortCheckerServiceInterface,
        gateway_initializer_service: GatewayInitializerServiceInterface,
        session_repository: SessionRepositoryInterface
    ) -> None:
        """Initialize the use case.

        Args:
            logger: Logger for recording events
            port_checker_service: Service for checking port availability
            gateway_initializer_service: Service for initializing gateway components
            session_repository: Repository for session management
        """
        self.logger = logger
        self.port_checker_service = port_checker_service
        self.gateway_initializer_service = gateway_initializer_service
        self.session_repository = session_repository
        
        # Gateway running state flag
        self.running = False
        
        # Signal handlers
        self._original_sigint_handler = None
        self._original_sigterm_handler = None

    def execute(self, is_threaded_mode: bool = False) -> bool:
        """Execute the run gateway use case.

        Args:
            is_threaded_mode: If True, adapts behavior to run in a thread context

        Returns:
            bool: True if gateway started successfully, False otherwise
        """
        try:
            # Check if user is logged in
            if not self.session_repository.is_user_logged_in():
                self.logger.log_info("User not logged in")
                print("Please login first (option 1)")
                return False
            
            # Check if required ports are available
            port_status = self.port_checker_service.check_port_availability()
            if not all(port_status.values()):
                self.logger.log_error("Required ports are not available")
                self._display_port_error(port_status)
                return False
            
            # Initialize gateway components
            if not self.gateway_initializer_service.initialize_components():
                self.logger.log_error("Failed to initialize gateway components")
                return False
            
            # Connect API callbacks to tick producer
            if not self.gateway_initializer_service.connect_api_callbacks():
                self.logger.log_error("Failed to connect API callbacks")
                self.gateway_initializer_service.cleanup_zmq()
                return False
            
            # Display information about the running gateway
            self._display_gateway_info()
            
            if not is_threaded_mode:
                print("\nThe gateway is now running. Press Ctrl+C to stop.")
            
            # Set running flag
            self.running = True
            
            # Start the main processing loop
            self._run_event_loop(is_threaded_mode)
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Failed to run gateway: {str(e)}")
            print(f"\nERROR: Gateway start failed: {str(e)}")
            return False
        finally:
            # Always clean up resources even if the event loop already
            # stopped and self.running is False. This ensures ZeroMQ
            # sockets are closed when the gateway exits normally or
            # due to an exception.
            self.gateway_initializer_service.cleanup_zmq()
            self.running = False

    def stop(self) -> None:
        """Stop the gateway gracefully."""
        self.logger.log_info("Stopping gateway gracefully")
        self.running = False

    def _run_event_loop(self, is_threaded_mode: bool) -> None:
        """Run the event processing loop to keep the gateway alive.

        Args:
            is_threaded_mode: If True, adapts behavior for running in a thread
        """
        try:
            # Register signal handlers for graceful shutdown - ONLY in main thread mode
            if not is_threaded_mode:
                self._setup_signal_handlers()
            
            self.logger.log_info("Gateway event loop started")
            
            # Simple loop that keeps the process alive
            while self.running:
                # Sleep to reduce CPU usage
                time.sleep(0.1)
                
                # Here additional periodic tasks could be added:
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
            self._restore_signal_handlers()
            self.logger.log_info("Gateway event loop terminated")

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        self._original_sigint_handler = signal.getsignal(signal.SIGINT)
        self._original_sigterm_handler = signal.getsignal(signal.SIGTERM)
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _restore_signal_handlers(self) -> None:
        """Restore original signal handlers."""
        if self._original_sigint_handler:
            signal.signal(signal.SIGINT, self._original_sigint_handler)
            
        if self._original_sigterm_handler:
            signal.signal(signal.SIGTERM, self._original_sigterm_handler)

    def _signal_handler(self, sig, frame) -> None:
        """Handle termination signals for graceful shutdown.

        Args:
            sig: Signal number
            frame: Current stack frame
        """
        self.logger.log_info(f"Received signal {sig}, initiating gateway shutdown")
        self.stop()

    def _display_port_error(self, port_status: Dict[int, bool]) -> None:
        """Display port error information to the user.
        
        Args:
            port_status: Dictionary with port numbers as keys and availability as values
        """
        print("\nERROR: One or more required ports are in use by other applications:")
        for port, available in port_status.items():
            if not available:
                print(f"- Port {port} is already in use")
        print("\nSolutions:")
        print("- Close other instances of this application")
        print("- Close any other applications using these ports")
        print("- Change the port configuration (requires code modification)")
        
    def _display_gateway_info(self) -> None:
        """Display information about the running gateway."""
        # Get connection addresses from the gateway initializer service
        tick_sub_address, signal_push_address = self.gateway_initializer_service.get_connection_addresses()
        
        print("\n=== ZeroMQ Market Data Gateway Initialized ===")
        print(f"Publishing ticks on: {tick_sub_address}")
        print(f"Receiving signals on: {signal_push_address}")
        print("\nTo complete the trading system, you need to:")
        print("1. Run the strategy process (run_strategy.py)")
        print("2. Run the order executor process (run_order_executor.py)")