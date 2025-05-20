"""ZeroMQ Puller Implementation."""

from typing import Optional, Tuple, Dict, Any
import zmq
import time

from src.interactor.interfaces.logger.logger import LoggerInterface


class ZmqPuller:
    """Handles receiving messages using ZeroMQ PULL socket."""

    def __init__(
        self,
        address: str,
        logger: Optional[LoggerInterface] = None,
        context: Optional[zmq.Context] = None,
        poll_timeout_ms: int = 10,  # Short timeout for responsiveness
        *,
        bind_mode: bool = True,
        connect_retry_attempts: int = 3,
        connect_retry_delay: float = 0.5,
    ) -> None:
        """Initialize the ZMQ Puller.

        Args:
            address: The address to bind the PULL socket to (e.g., "tcp://127.0.0.1:5556").
                     Note: PULL binds, PUSH connects in typical pipeline pattern.
            logger: Optional logger instance.
            context: Optional ZeroMQ context. If None, a new one is created.
            poll_timeout_ms: Timeout in milliseconds for polling the socket.
            bind_mode: If True, binds the socket; if False, connects to an existing endpoint.
            connect_retry_attempts: Number of times to retry binding if it fails.
            connect_retry_delay: Delay in seconds between binding attempts.
        """
        self._address = address
        self._logger = logger
        self._context = context or zmq.Context.instance()
        self._socket: Optional[zmq.Socket] = None
        self._poller = zmq.Poller()
        self._poll_timeout_ms = poll_timeout_ms
        self._bind_mode = bind_mode
        self._is_initialized = False
        self._connect_retry_attempts = connect_retry_attempts
        self._connect_retry_delay = connect_retry_delay
        self._init_socket()

    def _init_socket(self) -> None:
        """Creates and binds the PULL socket with retry mechanism."""
        if self._logger:
            self._logger.log_info(f"Initializing ZMQ Puller socket for {self._address}")

        attempt = 0
        while attempt < self._connect_retry_attempts and not self._is_initialized:
            try:
                # Cleanup any existing socket before creating a new one
                if self._socket:
                    try:
                        if self._poller:
                            self._poller.unregister(self._socket)
                        self._socket.close()
                    except zmq.ZMQError as init_error:
                        if self._logger:
                            self._logger.log_warning(
                                f"Error closing socket during init: {str(init_error)}"
                            )
                    except Exception as socket_cleanup_error:
                        if self._logger:
                            self._logger.log_warning(
                                f"Unexpected error during socket cleanup: {str(socket_cleanup_error)}"
                            )
                    self._socket = None

                # Reset poller
                self._poller = zmq.Poller()

                # Create new socket
                self._socket = self._context.socket(zmq.PULL)

                # Set socket options for better reliability
                self._socket.setsockopt(zmq.LINGER, 0)  # Don't wait on close
                self._socket.setsockopt(zmq.RCVHWM, 1000)  # High water mark

                # Attempt to bind / connect depending on mode
                attempt += 1
                if self._logger:
                    self._logger.log_info(
                        (
                            f"{'Binding' if self._bind_mode else 'Connecting'} to {self._address} "
                            f"(attempt {attempt}/{self._connect_retry_attempts})"
                        )
                    )

                if self._bind_mode:
                    self._socket.bind(self._address)
                else:
                    self._socket.connect(self._address)

                # Register with poller
                self._poller.register(self._socket, zmq.POLLIN)

                # Allow time for socket to establish
                time.sleep(0.1)

                self._is_initialized = True
                if self._logger:
                    self._logger.log_info(
                        f"ZMQ Puller socket successfully {'bound' if self._bind_mode else 'connected'} to {self._address}"
                    )
                break

            except zmq.ZMQError as e:
                if self._logger:
                    self._logger.log_error(
                        f"Failed to {'bind' if self._bind_mode else 'connect'} ZMQ Puller socket "
                        f"to {self._address}: {str(e)}"
                    )
                # Close socket if it was created but failed to bind
                if self._socket:
                    try:
                        self._socket.close()
                    except zmq.ZMQError as close_error:
                        if self._logger:
                            self._logger.log_warning(
                                f"Error closing socket after failed bind: {str(close_error)}"
                            )
                    except Exception as socket_cleanup_error:
                        if self._logger:
                            self._logger.log_warning(
                                f"Unexpected error during socket cleanup: {str(socket_cleanup_error)}"
                            )
                    self._socket = None

                # Only sleep between retries, not after the last attempt
                if attempt < self._connect_retry_attempts:
                    if self._logger:
                        self._logger.log_info(f"Retrying in {self._connect_retry_delay} seconds...")
                    time.sleep(self._connect_retry_delay)

        if not self._is_initialized:
            if self._logger:
                self._logger.log_error(
                    f"Failed to initialize ZMQ Puller after {self._connect_retry_attempts} attempts"
                )

    def receive(self, non_blocking: bool = False) -> Optional[bytes]:
        """Receive a message.

        Args:
            non_blocking: If True, polls the socket once with timeout.
                          If False (default), waits indefinitely (use with caution or in dedicated threads).

        Returns:
            The message payload in bytes if a message is received, otherwise None.
            Returns None immediately if non_blocking is True and no message is available.
        """
        # If not initialized, try to reinitialize
        if not self._is_initialized:
            self._init_socket()

        if self._is_initialized and self._socket and self._poller:
            try:
                if non_blocking:
                    socks = dict(self._poller.poll(self._poll_timeout_ms))
                    if self._socket in socks and socks[self._socket] == zmq.POLLIN:
                        message = self._socket.recv()
                        return message
                    else:
                        return None  # No message available within timeout
                else:
                    # Blocking receive - waits indefinitely
                    message = self._socket.recv()
                    return message
            except zmq.ZMQError as e:
                if self._logger:
                    # Avoid logging errors on normal termination (e.g., context terminated)
                    if e.errno != zmq.ETERM:
                        self._logger.log_error(f"Error receiving message: {str(e)}")
                # Socket may be in a bad state - try to reinitialize for next attempt
                self._is_initialized = False
                return None
            except Exception as e:  # Catch other potential errors
                if self._logger:
                    self._logger.log_error(f"Unexpected error during ZMQ receive: {str(e)}")
                return None
        else:
            if self._logger:
                self._logger.log_warning("ZMQ Puller socket is not initialized. Cannot receive.")
            return None

    def close(self) -> None:
        """Closes the ZeroMQ socket."""
        if self._socket:
            try:
                if self._poller:
                    self._poller.unregister(self._socket)
                self._socket.close()
                self._is_initialized = False
                if self._logger:
                    self._logger.log_info("ZMQ Puller socket closed.")
            except zmq.ZMQError as close_error:
                if self._logger:
                    self._logger.log_error(f"Error closing ZMQ Puller socket: {str(close_error)}")
            except Exception as unregister_error:
                if self._logger:
                    self._logger.log_warning(
                        f"Error unregistering poller for ZMQ Puller: {str(unregister_error)}"
                    )
            finally:
                self._socket = None
                self._poller = None  # type: ignore
