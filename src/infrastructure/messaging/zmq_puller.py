"""ZeroMQ Puller Implementation."""
import zmq
from typing import Optional

from src.interactor.interfaces.logger.logger import LoggerInterface


class ZmqPuller:
    """Handles receiving messages using ZeroMQ PULL socket."""

    def __init__(
        self,
        bind_to_address: str,
        logger: Optional[LoggerInterface] = None,
        context: Optional[zmq.Context] = None,
        poll_timeout_ms: int = 10  # Short timeout for responsiveness
    ):
        """Initialize the ZMQ Puller.

        Args:
            bind_to_address: The address to bind the PULL socket to (e.g., "tcp://*:5556").
                             Note: PULL binds, PUSH connects in typical pipeline pattern.
            logger: Optional logger instance.
            context: Optional ZeroMQ context. If None, a new one is created.
            poll_timeout_ms: Timeout in milliseconds for polling the socket.
        """
        self._address = bind_to_address
        self._logger = logger
        self._context = context or zmq.Context.instance()
        self._socket: Optional[zmq.Socket] = None
        self._poller = zmq.Poller()
        self._poll_timeout_ms = poll_timeout_ms
        self._initialize_socket()

    def _initialize_socket(self) -> None:
        """Creates and binds the PULL socket."""
        try:
            self._socket = self._context.socket(zmq.PULL)
            self._socket.bind(self._address)
            if self._logger:
                self._logger.log_info(f"ZMQ Puller bound to {self._address}")
            self._poller.register(self._socket, zmq.POLLIN)
        except zmq.ZMQError as e:
            if self._logger:
                self._logger.log_error(f"Failed to bind ZMQ Puller to {self._address}: {e}")
            self._socket = None
            self._poller = None # type: ignore
            raise

    def receive(self, non_blocking: bool = False) -> Optional[bytes]:
        """Receive a message.

        Args:
            non_blocking: If True, polls the socket once with timeout. 
                          If False (default), waits indefinitely (use with caution or in dedicated threads).

        Returns:
            The message payload in bytes if a message is received, otherwise None.
            Returns None immediately if non_blocking is True and no message is available.
        """
        if not self._socket or not self._poller:
            if self._logger:
                self._logger.log_warning("ZMQ Puller socket/poller not initialized. Cannot receive.")
            return None

        try:
            if non_blocking:
                socks = dict(self._poller.poll(self._poll_timeout_ms))
                if self._socket in socks and socks[self._socket] == zmq.POLLIN:
                    message = self._socket.recv()
                    return message
                else:
                    return None # No message available within timeout
            else:
                # Blocking receive - waits indefinitely
                message = self._socket.recv()
                return message
        except zmq.ZMQError as e:
            if self._logger:
                 # Avoid logging errors on normal termination (e.g., context terminated)
                if e.errno != zmq.ETERM:
                    self._logger.log_error(f"Error receiving message: {e}")
            return None
        except Exception as e: # Catch other potential errors
            if self._logger:
                self._logger.log_error(f"Unexpected error during ZMQ receive: {e}")
            return None

    def close(self) -> None:
        """Closes the ZeroMQ socket."""
        if self._socket:
            try:
                self._poller.unregister(self._socket)
                self._socket.close()
                if self._logger:
                    self._logger.log_info("ZMQ Puller socket closed.")
            except zmq.ZMQError as e:
                 if self._logger:
                    self._logger.log_error(f"Error closing ZMQ Puller socket: {e}")
            except Exception as e:
                if self._logger:
                    self._logger.log_warning(f"Error unregistering poller for ZMQ Puller: {e}")
            finally:
                self._socket = None
                self._poller = None # type: ignore 