"""ZeroMQ Subscriber Implementation."""
import zmq
from typing import Optional, Tuple, List

from src.interactor.interfaces.logger.logger import LoggerInterface


class ZmqSubscriber:
    """Handles receiving messages using ZeroMQ SUB socket."""

    def __init__(
        self,
        connect_to_address: str,
        topics: List[bytes],
        logger: Optional[LoggerInterface] = None,
        context: Optional[zmq.Context] = None,
        poll_timeout_ms: int = 10  # Short timeout for responsiveness
    ):
        """Initialize the ZMQ Subscriber.

        Args:
            connect_to_address: The address of the PUB socket to connect to (e.g., "tcp://localhost:5555").
            topics: A list of topics (bytes) to subscribe to. Use [b""] to subscribe to all.
            logger: Optional logger instance.
            context: Optional ZeroMQ context. If None, a new one is created.
            poll_timeout_ms: Timeout in milliseconds for polling the socket.
        """
        self._address = connect_to_address
        self._topics = topics
        self._logger = logger
        self._context = context or zmq.Context.instance()
        self._socket: Optional[zmq.Socket] = None
        self._poller = zmq.Poller()
        self._poll_timeout_ms = poll_timeout_ms
        self._initialize_socket()

    def _initialize_socket(self) -> None:
        """Creates, connects, and subscribes the SUB socket."""
        try:
            self._socket = self._context.socket(zmq.SUB)
            self._socket.connect(self._address)
            if not self._topics:
                if self._logger:
                    self._logger.log_warning("No topics provided to ZMQ Subscriber, subscribing to all (using b'').")
                self._socket.subscribe(b"") # Subscribe to all if empty list provided
            else:
                for topic in self._topics:
                    self._socket.subscribe(topic)
                    if self._logger:
                        self._logger.log_info(f"ZMQ Subscriber subscribed to topic: {topic.decode() if isinstance(topic, bytes) else topic} at {self._address}")
            self._poller.register(self._socket, zmq.POLLIN)
        except zmq.ZMQError as e:
            if self._logger:
                self._logger.log_error(f"Failed to connect/subscribe ZMQ Subscriber to {self._address}: {e}")
            self._socket = None
            self._poller = None # type: ignore
            raise

    def receive(self, non_blocking: bool = False) -> Optional[Tuple[bytes, bytes]]:
        """Receive a message (topic, payload).

        Args:
            non_blocking: If True, polls the socket once with timeout. 
                          If False (default), waits indefinitely (use with caution or in dedicated threads).

        Returns:
            A tuple (topic, message) in bytes if a message is received, otherwise None.
            Returns None immediately if non_blocking is True and no message is available.
        """
        if not self._socket or not self._poller:
            if self._logger:
                self._logger.log_warning("ZMQ Subscriber socket/poller not initialized. Cannot receive.")
            return None

        try:
            if non_blocking:
                socks = dict(self._poller.poll(self._poll_timeout_ms))
                if self._socket in socks and socks[self._socket] == zmq.POLLIN:
                    topic, message = self._socket.recv_multipart()
                    return topic, message
                else:
                    return None # No message available within timeout
            else:
                # Blocking receive - waits indefinitely
                topic, message = self._socket.recv_multipart()
                return topic, message
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
                    self._logger.log_info("ZMQ Subscriber socket closed.")
            except zmq.ZMQError as e:
                 if self._logger:
                    self._logger.log_error(f"Error closing ZMQ Subscriber socket: {e}")
            except Exception as e:
                if self._logger:
                    self._logger.log_warning(f"Error unregistering poller for ZMQ Subscriber: {e}")
            finally:
                self._socket = None
                self._poller = None # type: ignore 