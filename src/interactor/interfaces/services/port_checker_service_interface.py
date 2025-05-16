"""Port Checker Service Interface.

This module defines the interface for the port checker service.
"""

from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class PortCheckerServiceInterface(Protocol):
    """Interface for the port checker service."""
    
    def check_port_availability(self) -> Dict[str, bool]:
        """Check if the required ports are available.

        Returns:
            Dict[str, bool]: Dictionary with port numbers as keys and availability as values
        """
        ...