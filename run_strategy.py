#!/usr/bin/env python
"""Strategy Process for Futures Trading Machine.

This script runs the Support Resistance Strategy in a separate process,
subscribing to market data ticks and publishing trading signals.
"""

import os
import sys
import time
import signal
import zmq
import argparse
from typing import Dict, Any, Optional

# Ensure the project root is in the path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.messaging import ZmqSubscriber, ZmqPusher, deserialize
from src.infrastructure.events.tick import TickEvent
from src.domain.strategy.support_resistance_strategy import SupportResistanceStrategy
from src.infrastructure.repositories.condition_in_memory_repository import (
    ConditionInMemoryRepository,
)
from src.infrastructure.loggers.logger_default import LoggerDefault


class StrategyProcess:
    """Process for running the Support Resistance Strategy."""

    def __init__(self, config_dict: Dict[str, Any]):
        """Initialize the strategy process.

        Args:
            config_dict: Configuration parameters including ZMQ addresses
        """
        self.config_dict = config_dict
        self.running = False
        self.logger = LoggerDefault()

        # Create ZMQ context
        self.context = zmq.Context.instance()

        # Initialize repositories
        self.condition_repository = ConditionInMemoryRepository()

        # Initialize ZMQ components
        self.tick_subscriber: Optional[ZmqSubscriber] = None
        self.signal_pusher: Optional[ZmqPusher] = None
        self.strategy: Optional[SupportResistanceStrategy] = None

        # Define poll timeout
        self.poll_timeout_ms = 100

    def start(self):
        """Start the strategy process."""
        try:
            self.logger.log_info("Starting strategy process...")

            # Initialize ZMQ components
            self._initialize_zmq()

            # Initialize strategy
            self._initialize_strategy()

            # Set running flag
            self.running = True

            # Register signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # Run the main loop
            self._run_loop()

        except Exception as e:
            self.logger.log_error(f"Error starting strategy process: {str(e)}")
            sys.exit(1)
        finally:
            self._cleanup()

    def _initialize_zmq(self):
        """Initialize ZMQ subscriber and pusher."""
        try:
            # Create subscriber to receive tick data
            # ZmqSubscriber constructor takes a list of topics in bytes
            self.tick_subscriber = ZmqSubscriber(
                connect_to_address=self.config_dict["tick_sub_address"],
                topics=[b""],  # Subscribe to all topics
                logger=self.logger,
                context=self.context,
                poll_timeout_ms=self.poll_timeout_ms,
            )
            self.logger.log_info(f"Subscribing to ticks at {self.config_dict['tick_sub_address']}")

            # Create pusher to send trading signals
            self.signal_pusher = ZmqPusher(
                self.config_dict["signal_push_address"], self.logger, self.context
            )
            self.logger.log_info(f"Pushing signals to {self.config_dict['signal_push_address']}")

        except Exception as e:
            self.logger.log_error(f"Failed to initialize ZMQ components: {str(e)}")
            raise

    def _initialize_strategy(self):
        """Initialize the strategy with repositories and ZMQ components."""
        try:
            # Create strategy
            self.strategy = SupportResistanceStrategy(
                condition_repository=self.condition_repository,
                signal_pusher=self.signal_pusher,
                logger=self.logger,
            )
            self.logger.log_info("Strategy initialized")

            # Load existing conditions from repository
            conditions = self.condition_repository.get_all()
            if conditions:
                self.logger.log_info(f"Loaded {len(conditions)} trading conditions")
            else:
                self.logger.log_warning(
                    "No trading conditions found. Create conditions before trading."
                )

        except Exception as e:
            self.logger.log_error(f"Failed to initialize strategy: {str(e)}")
            raise

    def _run_loop(self):
        """Run the main processing loop."""
        self.logger.log_info("Entering main processing loop")
        print("Strategy process started. Waiting for market data...")
        print("Press Ctrl+C to stop.")

        try:
            while self.running:
                try:
                    # Receive message with non-blocking mode
                    message_data = self.tick_subscriber.receive(non_blocking=True)

                    # Process message if received
                    if message_data is not None:
                        # Based on ZmqSubscriber implementation, receive() returns (topic, message) tuple
                        topic, message = message_data

                        # Deserialize tick event from the message
                        tick_event = deserialize(message)

                        if isinstance(tick_event, TickEvent):
                            # Process tick event in strategy
                            self.strategy.process_tick_event(tick_event)
                        else:
                            self.logger.log_warning(
                                f"Received non-TickEvent message: {type(tick_event)}"
                            )

                    # Small sleep to prevent CPU hogging in the loop
                    # since we're using non-blocking mode
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
        self.logger.log_info("Cleaning up strategy process resources...")

        # Close strategy
        if self.strategy:
            try:
                self.strategy.close()
                self.logger.log_info("Strategy closed")
            except Exception as e:
                self.logger.log_error(f"Error closing strategy: {str(e)}")

        # Close ZMQ components
        if self.tick_subscriber:
            try:
                self.tick_subscriber.close()
                self.logger.log_info("Tick subscriber closed")
            except Exception as e:
                self.logger.log_error(f"Error closing tick subscriber: {str(e)}")

        if self.signal_pusher:
            try:
                self.signal_pusher.close()
                self.logger.log_info("Signal pusher closed")
            except Exception as e:
                self.logger.log_error(f"Error closing signal pusher: {str(e)}")

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
        self.logger.log_info(f"Received signal {sig}, shutting down strategy process")
        self.running = False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the trading strategy process")

    # Default values - these could be read from a config file instead
    default_tick_sub = "tcp://localhost:5555"
    default_signal_push = "tcp://localhost:5556"

    # Add arguments
    parser.add_argument(
        "--tick-address",
        default=default_tick_sub,
        help=f"ZMQ address to subscribe for tick data (default: {default_tick_sub})",
    )
    parser.add_argument(
        "--signal-address",
        default=default_signal_push,
        help=f"ZMQ address to push trading signals (default: {default_signal_push})",
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()

    # Create config dictionary
    config = {"tick_sub_address": args.tick_address, "signal_push_address": args.signal_address}

    # Create and start strategy process
    process = StrategyProcess(config)
    process.start()
