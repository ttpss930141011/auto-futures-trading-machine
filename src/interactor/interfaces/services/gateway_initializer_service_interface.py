"""Gateway Initializer Service Interface.

This module defines the interface for the gateway initializer service.

Note: This interface intentionally avoids importing infrastructure types
(e.g., ZmqPublisher, TickProducer) to respect the Dependency Rule in
Clean Architecture — inner layers must not depend on outer layers.
"""

from typing import Protocol, Tuple, runtime_checkable


@runtime_checkable
class GatewayInitializerServiceInterface(Protocol):
    """Interface for the gateway initializer service."""

    def initialize_components(self) -> bool:
        """Initialize ZMQ components for the gateway.

        Returns:
            bool: True if initialization was successful, False otherwise
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
