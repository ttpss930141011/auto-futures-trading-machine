#!/usr/bin/env python
"""Order Executor Process with DLL Gateway integration.

This script runs the OrderExecutor in a separate process,
receiving trading signals and executing market orders through
the centralized DLL Gateway Service.
"""

import sys
import time
import signal
import zmq
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

# Ensure the project root is in the path so imports work correctly
sys.path.append(str(Path(__file__).resolve().parent))

from src.infrastructure.messaging import ZmqPuller
from src.domain.order.order_executor_gateway import OrderExecutorGateway
from src.infrastructure.services.dll_gateway_client import DllGatewayClient
from src.infrastructure.repositories.session_json_file_repository import SessionJsonFileRepository
from src.infrastructure.loggers.logger_default import LoggerDefault
from src.app.cli_pfcf.config import Config


class OrderExecutorGatewayProcess:
    """Process running the order executor with DLL Gateway integration.

    This process eliminates the need for DLL initialization in child processes
    by communicating with the centralized DLL Gateway Server.
    Follows Single Responsibility Principle by focusing on signal processing only.
    """

    def __init__(self, config_dict: Dict[str, Any]):
        """Initialize the order executor gateway process.

        Args:
            config_dict: Configuration parameters including ZMQ addresses.
        """
        self._config_dict = config_dict
        self._running = False
        self._logger = LoggerDefault()

        # Define polling timeout (in milliseconds)
        self._poll_timeout_ms = 100

        # Create ZMQ context
        self._context = zmq.Context.instance()

        # Initialize session repository (read-only for session info)
        self._session_repository = SessionJsonFileRepository(
            session_timeout=3600  # Default timeout
        )

        # Initialize basic config to get gateway settings
        from src.app.cli_pfcf.config import Config

        basic_config = Config(None)  # We don't need exchange_api for getting addresses

        # Initialize DLL Gateway Client
        self._dll_gateway_client = DllGatewayClient(
            server_address=config_dict.get(
                "dll_gateway_address", basic_config.DLL_GATEWAY_CONNECT_ADDRESS
            ),
            logger=self._logger,
            timeout_ms=basic_config.DLL_GATEWAY_REQUEST_TIMEOUT_MS,
            retry_count=basic_config.DLL_GATEWAY_RETRY_COUNT,
        )

        # Initialize ZMQ components
        self._signal_puller: Optional[ZmqPuller] = None
        self._order_executor: Optional[OrderExecutorGateway] = None

    def start(self) -> None:
        """Start the order executor gateway process."""
        try:
            self._logger.log_info("Starting order executor gateway process...")

            # Check session status
            if not self._check_session_status():
                self._logger.log_error(
                    "Session not initialized. Please ensure user is logged in through main application."
                )
                print("ERROR: Session not initialized. Run the main application and login first.")
                sys.exit(1)

            # Check DLL Gateway connectivity
            if not self._check_gateway_connectivity():
                self._logger.log_error(
                    "DLL Gateway is not accessible. Please ensure main application is running."
                )
                print("ERROR: DLL Gateway is not accessible.")
                sys.exit(1)

            # Initialize ZMQ components
            self._initialize_zmq()

            # Initialize order executor
            self._initialize_order_executor()

            # Set running flag
            self._running = True

            # Register signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # Run the main loop
            self._run_loop()

        except Exception as e:
            self._logger.log_error(f"Error starting order executor gateway process: {str(e)}")
            sys.exit(1)
        finally:
            self._cleanup()

    def _check_session_status(self) -> bool:
        """Check if user session is properly initialized.

        Returns:
            bool: True if session is initialized, False otherwise.
        """
        try:
            # Check if user is logged in
            if not self._session_repository.is_user_logged_in():
                self._logger.log_error("User is not logged in")
                return False

            # Check if order account is selected
            order_account = self._session_repository.get_order_account()
            if not order_account:
                self._logger.log_error("No order account selected")
                return False

            self._logger.log_info(f"Session validated. Order account: {order_account}")
            return True

        except Exception as e:
            self._logger.log_error(f"Error checking session status: {e}")
            return False

    def _check_gateway_connectivity(self) -> bool:
        """Check if DLL Gateway is accessible.

        Returns:
            bool: True if gateway is accessible, False otherwise.
        """
        try:
            # Test gateway connectivity with health check
            health_status = self._dll_gateway_client.get_health_status()

            if health_status.get("status") == "healthy":
                self._logger.log_info("DLL Gateway connectivity verified")
                return True
            else:
                self._logger.log_error(f"DLL Gateway unhealthy: {health_status}")
                return False

        except Exception as e:
            self._logger.log_error(f"Error checking gateway connectivity: {e}")
            return False

    def _initialize_zmq(self) -> None:
        """Initialize ZMQ puller for trading signals."""
        try:
            # Create puller to receive trading signals
            self._signal_puller = ZmqPuller(
                address=self._config_dict["signal_pull_address"],
                logger=self._logger,
                context=self._context,
                poll_timeout_ms=self._poll_timeout_ms,
            )
            self._logger.log_info(
                f"Pulling signals from {self._config_dict['signal_pull_address']}"
            )

        except Exception as e:
            self._logger.log_error(f"Failed to initialize ZMQ components: {str(e)}")
            raise

    def _initialize_order_executor(self) -> None:
        """Initialize the order executor with DLL Gateway integration."""
        try:
            # Create order executor with gateway client
            self._order_executor = OrderExecutorGateway(
                signal_puller=self._signal_puller,
                dll_gateway_service=self._dll_gateway_client,
                session_repository=self._session_repository,
                logger=self._logger,
                default_quantity=1,
            )
            self._logger.log_info("Order executor with gateway integration initialized")

        except Exception as e:
            self._logger.log_error(f"Failed to initialize order executor: {str(e)}")
            raise

    def _run_loop(self) -> None:
        """Run the main processing loop.

        Continuously polls for trading signals and delegates processing
        to OrderExecutorGateway. Sleeps briefly when no message is received.
        """
        self._logger.log_info("Entering main processing loop with gateway integration")
        print("Order executor gateway process started. Waiting for trading signals...")
        print("This process communicates with DLL Gateway Server in the main application.")
        print("Press Ctrl+C to stop.")

        try:
            while self._running:
                try:
                    processed = self._order_executor.process_received_signal()
                    if not processed:
                        time.sleep(self._poll_timeout_ms / 1000.0)
                except zmq.ZMQError as e:
                    self._logger.log_error(f"ZMQ error in main loop: {e}")
                    if getattr(e, "errno", None) == zmq.ETERM:
                        break
                except Exception as e:
                    self._logger.log_error(f"Error in main loop: {e}")
        except KeyboardInterrupt:
            self._logger.log_info("Keyboard interrupt received")
        finally:
            self._running = False

    def _cleanup(self) -> None:
        """Clean up resources."""
        self._logger.log_info("Cleaning up order executor gateway process resources...")

        # Close order executor
        if self._order_executor:
            try:
                self._order_executor.close()
                self._logger.log_info("Order executor closed")
            except Exception as e:
                self._logger.log_error(f"Error closing order executor: {str(e)}")

        # Close DLL Gateway client
        if self._dll_gateway_client:
            try:
                self._dll_gateway_client.close()
                self._logger.log_info("DLL Gateway client closed")
            except Exception as e:
                self._logger.log_error(f"Error closing DLL Gateway client: {str(e)}")

        # Close ZMQ components
        if self._signal_puller:
            try:
                self._signal_puller.close()
                self._logger.log_info("Signal puller closed")
            except Exception as e:
                self._logger.log_error(f"Error closing signal puller: {str(e)}")

        # Close ZMQ context
        if self._context and not self._context.closed:
            try:
                self._context.term()
                self._logger.log_info("ZMQ context terminated")
            except Exception as e:
                self._logger.log_error(f"Error terminating ZMQ context: {str(e)}")

    def _signal_handler(self, sig, frame):
        """Handle termination signals.

        Args:
            sig: Signal number.
            frame: Current stack frame.
        """
        self._logger.log_info(
            f"Received signal {sig}, shutting down order executor gateway process"
        )
        self._running = False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the order executor process with DLL Gateway")

    # Get default values from config
    from src.app.cli_pfcf.config import Config

    basic_config = Config(None)  # We don't need exchange_api for getting addresses

    default_signal_pull = basic_config.ZMQ_SIGNAL_PULL_ADDRESS
    default_dll_gateway = basic_config.DLL_GATEWAY_CONNECT_ADDRESS

    # Add arguments
    parser.add_argument(
        "--signal-address",
        default=default_signal_pull,
        help=f"ZMQ address to pull trading signals from (default: {default_signal_pull})",
    )

    parser.add_argument(
        "--gateway-address",
        default=default_dll_gateway,
        help=f"ZMQ address of DLL Gateway Server (default: {default_dll_gateway})",
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()

    # Create config dictionary
    config = {
        "signal_pull_address": args.signal_address,
        "dll_gateway_address": args.gateway_address,
    }

    # Create and start order executor gateway process
    process = OrderExecutorGatewayProcess(config)
    process.start()
