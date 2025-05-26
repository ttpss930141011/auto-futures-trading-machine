"""Gateway Initializer Service Interface.

This module defines the interface for the gateway initializer service.
"""

from typing import Protocol, Optional, Tuple, runtime_checkable

from src.infrastructure.messaging import ZmqPublisher
from src.infrastructure.pfcf_client.tick_producer import TickProducer


@runtime_checkable
class GatewayInitializerServiceInterface(Protocol):
    """Interface for the gateway initializer service."""

    def initialize_components(self) -> bool:
        """Initialize ZMQ components for the gateway.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        ...

    def get_components(self) -> Tuple[Optional[ZmqPublisher], Optional[TickProducer]]:
        """Get the initialized ZMQ components.

        Returns:
            Tuple containing the tick publisher and tick producer
        """
        ...

    def connect_api_callbacks(self) -> bool:
        """Connect exchange API callbacks to the tick producer.

        Returns:
            bool: True if callbacks were successfully connected, False otherwise
        """
        ...

    def cleanup_zmq(self) -> None:
        """Close ZMQ sockets and terminate context gracefully."""
        ...

    def get_connection_addresses(self) -> Tuple[str, str]:
        """Get the ZMQ connection addresses for client applications.

        Returns:
            Tuple containing the tick subscriber address and signal push address
        """
        ...

    @property
    def is_initialized(self) -> bool:
        """Check if the gateway components are initialized.

        Returns:
            bool: True if initialized, False otherwise
        """
        ...
