#!/usr/bin/env python
"""Order Executor Process for Futures Trading Machine.

This script runs the OrderExecutor in a separate process,
receiving trading signals and executing market orders.
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
from src.domain.order.order_executor import OrderExecutor
from src.infrastructure.repositories.session_json_file_repository import SessionJsonFileRepository
from src.infrastructure.loggers.logger_default import LoggerDefault
from src.app.cli_pfcf.config import Config
from src.infrastructure.pfcf_client.api import PFCFApi
from src.interactor.use_cases.send_market_order import SendMarketOrderUseCase
from src.app.cli_pfcf.presenters.send_market_order_presenter import SendMarketOrderPresenter


class OrderExecutorProcess:
    """Process running the order executor.

    Continuously pulls trading signals via ZMQ and delegates processing to OrderExecutor."""

    def __init__(self, config_dict: Dict[str, Any]):
        """Initialize the order executor process.

        Args:
            config_dict: Configuration parameters including ZMQ addresses
        """
        self.config_dict = config_dict
        self.running = False
        self.logger = LoggerDefault()

        # Define polling timeout (in milliseconds)
        self.poll_timeout_ms = 100

        # Create ZMQ context
        self.context = zmq.Context.instance()

        # Initialize API and config
        self.exchange_api = PFCFApi()
        self.config = Config(self.exchange_api)

        # Initialize repositories
        self.session_repository = SessionJsonFileRepository(self.config.DEFAULT_SESSION_TIMEOUT)

        # Initialize use case
        self.presenter = SendMarketOrderPresenter()
        self.send_market_order_use_case = SendMarketOrderUseCase(
            self.presenter, self.config, self.logger, self.session_repository
        )

        # Initialize ZMQ components
        self.signal_puller: Optional[ZmqPuller] = None
        self.order_executor: Optional[OrderExecutor] = None

    def start(self):
        """Start the order executor process."""
        try:
            self.logger.log_info("Starting order executor process...")

            # Check session status - this would normally get data from shared storage in a real app
            if not self._check_session_status():
                self.logger.log_error(
                    "Session not initialized. Please ensure user is logged in and item is registered."
                )
                print(
                    "ERROR: Session not initialized. Run the main application and set up user session first."
                )
                sys.exit(1)

            # Authenticate the exchange client for this process
            if not self._authenticate_exchange_client():
                self.logger.log_error(
                    "Failed to authenticate exchange client. Please ensure user is logged in in the main application."
                )
                print("ERROR: Failed to authenticate exchange client.")
                sys.exit(1)

            # Initialize ZMQ components
            self._initialize_zmq()

            # Initialize order executor
            self._initialize_order_executor()

            # Set running flag
            self.running = True

            # Register signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # Run the main loop
            self._run_loop()

        except Exception as e:
            self.logger.log_error(f"Error starting order executor process: {str(e)}")
            sys.exit(1)
        finally:
            self._cleanup()

    def _check_session_status(self) -> bool:
        """Check if user session is properly initialized.

        In a real application, this might read session info from a shared database or file.
        For now, we just check basic requirements.

        Returns:
            bool: True if session is initialized, False otherwise
        """
        # In a real application, check if user is logged in from a shared data source
        # For now, just check if we have the necessary session information

        # In a distributed system, you should implement proper session sharing
        # This is a placeholder that would need to be replaced with actual shared session management
        return True

    def _authenticate_exchange_client(self) -> bool:
        """Authenticate the exchange client for this process.

        Returns:
            bool: True if authentication is successful, False otherwise
        """
        try:
            # Read session data to get user account
            session_data = self.session_repository._read_data()
            if not session_data or not session_data.get("logged_in"):
                self.logger.log_error("No active session found")
                return False

            user_account = session_data.get("account")
            if not user_account:
                self.logger.log_error("No user account found in session")
                return False

            # TEMPORARY: Get auth details for development
            # In production, use secure credential management
            auth_details = None
            if hasattr(self.session_repository, "get_auth_details"):
                auth_details = self.session_repository.get_auth_details()

            if not auth_details:
                self.logger.log_error(
                    "No authentication details available. "
                    "Please login through the main application first."
                )
                return False

            # Perform the actual login
            try:
                self.logger.log_info(f"Authenticating exchange client for account: {user_account}")
                self.config.EXCHANGE_CLIENT.PFCLogin(
                    user_account, auth_details["password"], auth_details["ip_address"]
                )

                # Verify login was successful by checking UserOrderSet
                order_set = self.config.EXCHANGE_CLIENT.UserOrderSet
                if order_set is not None:
                    self.logger.log_info(
                        f"Exchange client authenticated successfully. "
                        f"Found {len(order_set)} order accounts."
                    )
                    return True
                else:
                    self.logger.log_error("Login appeared successful but no order accounts found")
                    return False

            except Exception as e:
                self.logger.log_error(f"Failed to authenticate with exchange: {str(e)}")
                return False

        except Exception as e:
            self.logger.log_error(f"Error during exchange authentication: {str(e)}")
            return False

    def _initialize_zmq(self):
        """Initialize ZMQ puller."""
        try:
            # Create puller to receive trading signals
            # Using proper initialization parameters based on ZmqPuller implementation
            self.signal_puller = ZmqPuller(
                address=self.config_dict["signal_pull_address"],
                logger=self.logger,
                context=self.context,
                poll_timeout_ms=self.poll_timeout_ms,
            )
            self.logger.log_info(f"Pulling signals from {self.config_dict['signal_pull_address']}")

        except Exception as e:
            self.logger.log_error(f"Failed to initialize ZMQ components: {str(e)}")
            raise

    def _initialize_order_executor(self):
        """Initialize the order executor with dependencies."""
        try:
            # Create order executor
            self.order_executor = OrderExecutor(
                signal_puller=self.signal_puller,
                send_order_use_case=self.send_market_order_use_case,
                session_repository=self.session_repository,
                logger=self.logger,
            )
            self.logger.log_info("Order executor initialized")

        except Exception as e:
            self.logger.log_error(f"Failed to initialize order executor: {str(e)}")
            raise

    def _run_loop(self):
        """Run the main processing loop.

        Continuously polls for trading signals and delegates processing to OrderExecutor.
        Sleeps briefly when no message is received.
        """
        self.logger.log_info("Entering main processing loop")
        print("Order executor process started. Waiting for trading signals...")
        print("Press Ctrl+C to stop.")

        try:
            while self.running:
                try:
                    processed = self.order_executor.process_received_signal()
                    if not processed:
                        time.sleep(self.poll_timeout_ms / 1000.0)
                except zmq.ZMQError as e:
                    self.logger.log_error(f"ZMQ error in main loop: {e}")
                    if getattr(e, "errno", None) == zmq.ETERM:
                        break
                except Exception as e:
                    self.logger.log_error(f"Error in main loop: {e}")
        except KeyboardInterrupt:
            self.logger.log_info("Keyboard interrupt received")
        finally:
            self.running = False

    def _cleanup(self):
        """Clean up resources."""
        self.logger.log_info("Cleaning up order executor process resources...")

        # Close order executor
        if self.order_executor:
            try:
                self.order_executor.close()
                self.logger.log_info("Order executor closed")
            except Exception as e:
                self.logger.log_error(f"Error closing order executor: {str(e)}")

        # Close ZMQ components
        if self.signal_puller:
            try:
                self.signal_puller.close()
                self.logger.log_info("Signal puller closed")
            except Exception as e:
                self.logger.log_error(f"Error closing signal puller: {str(e)}")

        # Close ZMQ context
        if self.context and not self.context.closed:
            try:
                self.context.term()
                self.logger.log_info("ZMQ context terminated")
            except Exception as e:
                self.logger.log_error(f"Error terminating ZMQ context: {str(e)}")

    def _signal_handler(self, sig, frame):
        """Handle termination signals.

        Args:
            sig: Signal number
            frame: Current stack frame
        """
        self.logger.log_info(f"Received signal {sig}, shutting down order executor process")
        self.running = False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the order executor process")

    # Default values - these could be read from a config file instead
    default_signal_pull = "tcp://localhost:5556"

    # Add arguments
    parser.add_argument(
        "--signal-address",
        default=default_signal_pull,
        help=f"ZMQ address to pull trading signals from (default: {default_signal_pull})",
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()

    # Create config dictionary
    config = {"signal_pull_address": args.signal_address}

    # Create and start order executor process
    process = OrderExecutorProcess(config)
    process.start()
