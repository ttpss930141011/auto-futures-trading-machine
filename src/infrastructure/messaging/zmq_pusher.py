"""ZeroMQ Pusher Implementation."""
import zmq
from typing import Optional

from src.interactor.interfaces.logger.logger import LoggerInterface


class ZmqPusher:
    """Handles sending messages using ZeroMQ PUSH socket."""

    def __init__(
        self,
        connect_to_address: str,
        logger: Optional[LoggerInterface] = None,
        context: Optional[zmq.Context] = None
    ):
        """Initialize the ZMQ Pusher.

        Args:
            connect_to_address: The address to connect the PUSH socket to (e.g., "tcp://localhost:5556").
                                Note: PUSH connects, PULL binds in typical pipeline pattern.
            logger: Optional logger instance.
            context: Optional ZeroMQ context. If None, a new one is created.
        """
        self._address = connect_to_address
        self._logger = logger
        self._context = context or zmq.Context.instance()
        self._socket: Optional[zmq.Socket] = None
        self._initialize_socket()

    def _initialize_socket(self) -> None:
        """Creates and connects the PUSH socket."""
        try:
            self._socket = self._context.socket(zmq.PUSH)
            self._socket.connect(self._address)
            if self._logger:
                self._logger.log_info(f"ZMQ Pusher connected to {self._address}")
        except zmq.ZMQError as e:
            if self._logger:
                self._logger.log_error(f"Failed to connect ZMQ Pusher to {self._address}: {e}")
            self._socket = None
            raise

    def send(self, message: bytes) -> None:
        """Send a message.

        Args:
            message: The message payload (bytes).
        """
        if self._socket:
            try:
                self._socket.send(message)
                # if self._logger: # Logging every send can be too verbose
                #     self._logger.log_debug("Pushed message")
            except zmq.ZMQError as e:
                if self._logger:
                    self._logger.log_error(f"Failed to push message: {e}")
        else:
            if self._logger:
                self._logger.log_warning("ZMQ Pusher socket is not initialized. Cannot send.")

    def close(self) -> None:
        """Closes the ZeroMQ socket."""
        if self._socket:
            try:
                self._socket.close()
                if self._logger:
                    self._logger.log_info("ZMQ Pusher socket closed.")
            except zmq.ZMQError as e:
                if self._logger:
                    self._logger.log_error(f"Error closing ZMQ Pusher socket: {e}")
            finally:
                self._socket = None
