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

from src.infrastructure.messaging import ZmqPuller, deserialize
from src.infrastructure.events.trading_signal import TradingSignal
from src.domain.order.order_executor import OrderExecutor
from src.domain.value_objects import OrderOperation, OpenClose, DayTrade, TimeInForce, OrderTypeEnum
from src.infrastructure.repositories.session_in_memory_repository import SessionInMemoryRepository
from src.infrastructure.loggers.logger_default import LoggerDefault
from src.app.cli_pfcf.config import Config
from src.infrastructure.pfcf_client.api import PFCFApi
from src.interactor.use_cases.send_market_order import SendMarketOrderUseCase
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto
from src.app.cli_pfcf.presenters.send_market_order_presenter import SendMarketOrderPresenter


class OrderExecutorProcess:
    """Process for running the Order Executor."""

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
        self.session_repository = SessionInMemoryRepository(self.config.DEFAULT_SESSION_TIMEOUT)

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
                bind_mode=False,  # Connect to the existing PULL endpoint
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
        """Run the main processing loop."""
        self.logger.log_info("Entering main processing loop")
        print("Order executor process started. Waiting for trading signals...")
        print("Press Ctrl+C to stop.")

        try:
            while self.running:
                try:
                    # Receive message using non-blocking mode instead of has_message
                    message = self.signal_puller.receive(non_blocking=True)

                    # Process the message if received
                    if message is not None:
                        # Deserialize trading signal
                        signal = deserialize(message)

                        if isinstance(signal, TradingSignal):
                            # Process signal in order executor
                            self.logger.log_info(
                                f"Received trading signal: {signal.action.name} for {signal.commodity_id}"
                            )
                            print(
                                f"Executing order: {signal.action.name} for {signal.commodity_id}"
                            )

                            # Create the input DTO for SendMarketOrderUseCase
                            # Based on src/app/cli_pfcf/controllers/send_market_order_controller.py
                            try:
                                # Get required parameters from the session
                                order_account = self.session_repository.get_order_account()
                                item_code = self.session_repository.get_item_code()

                                if not order_account or not item_code:
                                    error_msg = "Missing order account or item code in session"
                                    self.logger.log_error(error_msg)
                                    print(f"Order execution failed: {error_msg}")
                                    continue

                                # Create the input DTO
                                input_dto = SendMarketOrderInputDto(
                                    order_account=order_account,
                                    item_code=item_code,
                                    side=signal.action,
                                    order_type=OrderTypeEnum.Market,
                                    price=0,  # market order does not need price
                                    quantity=1,  # Default quantity, could be retrieved from signal
                                    open_close=OpenClose.AUTO,
                                    note="Automated order from trading strategy",
                                    day_trade=DayTrade.No,
                                    time_in_force=TimeInForce.IOC,
                                )

                                # Execute the order
                                result = self.send_market_order_use_case.execute(input_dto)

                                if result.is_success:
                                    self.logger.log_info(
                                        f"Order executed successfully: {result.message}"
                                    )
                                    print(f"Order executed successfully: {result.message}")
                                else:
                                    self.logger.log_error(
                                        f"Order execution failed: {result.message}"
                                    )
                                    print(f"Order execution failed: {result.message}")
                            except Exception as e:
                                self.logger.log_error(f"Error executing order: {str(e)}")
                                print(f"Error executing order: {str(e)}")
                        else:
                            self.logger.log_warning(
                                f"Received non-TradingSignal message: {type(signal)}"
                            )

                    # Small sleep to prevent CPU hogging when using non-blocking mode
                    time.sleep(0.001)

                except zmq.ZMQError as e:
                    self.logger.log_error(f"ZMQ error in main loop: {str(e)}")
                    if e.errno == zmq.ETERM:
                        # Context was terminated
                        break
                except Exception as e:
                    self.logger.log_error(f"Error in main loop: {str(e)}")
                    # Continue processing despite errors

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
