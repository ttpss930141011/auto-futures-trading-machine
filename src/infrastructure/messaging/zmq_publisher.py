"""ZeroMQ Publisher Implementation."""

from typing import Any, Optional, Dict, Union
import time
import json
import zmq
from src.interactor.interfaces.logger.logger import LoggerInterface


class ZmqPublisher:
    """Publisher class for ZeroMQ PUB socket pattern."""

    def __init__(
        self,
        address: str,
        logger: Optional[LoggerInterface] = None,
        context: Optional[zmq.Context] = None,
        connect_retry_attempts: int = 3,
        connect_retry_delay: float = 0.5,
    ) -> None:
        """Initialize a ZeroMQ publisher.

        Args:
            address: The address to bind the publisher to.
            logger: Optional logger for recording events.
            context: Optional ZeroMQ context. If not provided, a new one is created.
            connect_retry_attempts: Number of times to retry binding if it fails.
            connect_retry_delay: Delay in seconds between binding attempts.
        """
        self._address = address
        self._logger = logger
        self._context = context if context else zmq.Context.instance()
        self._socket: Optional[zmq.Socket] = None
        self._is_initialized = False
        self._connect_retry_attempts = connect_retry_attempts
        self._connect_retry_delay = connect_retry_delay
        self._init_socket()

    def _init_socket(self) -> None:
        """Initialize the ZeroMQ PUB socket with retry mechanism.

        Handles creation, configuration, and binding of the socket.
        """
        if self._logger:
            self._logger.log_info(f"Initializing ZMQ Publisher socket for {self._address}")

        attempt = 0
        while attempt < self._connect_retry_attempts and not self._is_initialized:
            try:
                # Cleanup any existing socket before creating a new one
                if self._socket:
                    try:
                        self._socket.close()
                    except zmq.ZMQError as e:
                        if self._logger:
                            self._logger.log_warning(
                                f"Error closing socket after failed bind: {str(e)}"
                            )
                    self._socket = None

                # Create new socket
                self._socket = self._context.socket(zmq.PUB)

                # Set socket options for better reliability
                self._socket.setsockopt(zmq.LINGER, 0)  # Don't wait on close
                self._socket.setsockopt(zmq.SNDHWM, 1000)  # High water mark

                # Attempt to bind
                attempt += 1
                if self._logger:
                    self._logger.log_info(
                        f"Binding to {self._address} (attempt {attempt}/{self._connect_retry_attempts})"
                    )

                self._socket.bind(self._address)

                # Allow time for socket to establish
                time.sleep(0.1)

                self._is_initialized = True
                if self._logger:
                    self._logger.log_info(
                        f"ZMQ Publisher socket successfully bound to {self._address}"
                    )
                break

            except zmq.ZMQError as e:
                if self._logger:
                    self._logger.log_error(
                        f"Failed to bind ZMQ Publisher socket to {self._address}: {str(e)}"
                    )
                # Close socket if it was created but failed to bind
                if self._socket:
                    try:
                        self._socket.close()
                    except (zmq.ZMQError, OSError):
                        pass
                    self._socket = None

                # Only sleep between retries, not after the last attempt
                if attempt < self._connect_retry_attempts:
                    if self._logger:
                        self._logger.log_info(f"Retrying in {self._connect_retry_delay} seconds...")
                    time.sleep(self._connect_retry_delay)

        if not self._is_initialized:
            if self._logger:
                self._logger.log_error(
                    f"Failed to initialize ZMQ Publisher after {self._connect_retry_attempts} attempts"
                )

    def publish(self, topic: bytes, message: Union[Dict[str, Any], bytes, str]) -> bool:
        """Publish a message on a specific topic.

        Args:
            topic: The topic to publish on (as bytes).
            message: The message data to publish.

        Returns:
            bool: True if published successfully, False otherwise.
        """
        # If not initialized, try to reinitialize
        if not self._is_initialized:
            self._init_socket()

        if self._is_initialized and self._socket:
            try:
                # Prepare message if not already bytes
                if isinstance(message, dict):

                    message_data = json.dumps(message).encode("utf-8")
                elif isinstance(message, str):
                    message_data = message.encode("utf-8")
                else:
                    message_data = message

                # Send multipart message with topic and data
                self._socket.send_multipart([topic, message_data])
                return True
            except zmq.ZMQError as e:
                if self._logger:
                    self._logger.log_error(f"Error publishing message: {str(e)}")
                # Socket may be in a bad state - try to reinitialize for next attempt
                self._is_initialized = False
                return False
        else:
            if self._logger:
                self._logger.log_warning("ZMQ Publisher socket is not initialized. Cannot publish.")
            return False

    def close(self) -> None:
        """Close the ZeroMQ socket."""
        if self._socket:
            try:
                self._socket.close()
                self._is_initialized = False
                if self._logger:
                    self._logger.log_info("ZMQ Publisher socket closed.")
            except zmq.ZMQError as e:
                if self._logger:
                    self._logger.log_error(f"Error closing ZMQ Publisher socket: {str(e)}")
            finally:
                self._socket = None
