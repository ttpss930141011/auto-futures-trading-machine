"""ZeroMQ Publisher Implementation."""
import zmq
import time
from typing import Any, Optional

from src.interactor.interfaces.logger.logger import LoggerInterface


class ZmqPublisher:
    """Handles publishing messages using ZeroMQ PUB socket."""

    def __init__(
        self,
        connect_to_address: str,
        logger: Optional[LoggerInterface] = None,
        context: Optional[zmq.Context] = None
    ):
        """Initialize the ZMQ Publisher.

        Args:
            connect_to_address: The address to bind the PUB socket to (e.g., "tcp://*:5555").
            logger: Optional logger instance.
            context: Optional ZeroMQ context. If None, a new one is created.
        """
        self._address = connect_to_address
        self._logger = logger
        self._context = context or zmq.Context.instance()
        self._socket: Optional[zmq.Socket] = None
        self._initialize_socket()

    def _initialize_socket(self) -> None:
        """Creates and binds the PUB socket."""
        try:
            self._socket = self._context.socket(zmq.PUB)
            self._socket.bind(self._address)
            if self._logger:
                self._logger.log_info(f"ZMQ Publisher bound to {self._address}")
            # Allow time for connections to establish
            time.sleep(0.5)
        except zmq.ZMQError as e:
            if self._logger:
                self._logger.log_error(f"Failed to bind ZMQ Publisher to {self._address}: {e}")
            self._socket = None
            raise

    def publish(self, topic: bytes, message: bytes) -> None:
        """Publish a message with a specific topic.

        Args:
            topic: The topic to associate with the message (bytes).
            message: The message payload (bytes).
        """
        if self._socket:
            try:
                self._socket.send_multipart([topic, message])
                # if self._logger: # Logging every publish can be too verbose
                #     self._logger.log_debug(f"Published message on topic {topic.decode()}")
            except zmq.ZMQError as e:
                if self._logger:
                    self._logger.log_error(f"Failed to publish message on topic {topic.decode()}: {e}")
        else:
            if self._logger:
                self._logger.log_warning("ZMQ Publisher socket is not initialized. Cannot publish.")

    def close(self) -> None:
        """Closes the ZeroMQ socket."""
        if self._socket:
            try:
                self._socket.close()
                if self._logger:
                    self._logger.log_info("ZMQ Publisher socket closed.")
            except zmq.ZMQError as e:
                 if self._logger:
                    self._logger.log_error(f"Error closing ZMQ Publisher socket: {e}")
            finally:
                self._socket = None 