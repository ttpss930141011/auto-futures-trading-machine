"""Process Manager Service Interface.

This module defines the interface for the process manager service.
"""

from typing import Protocol, Optional, runtime_checkable
import subprocess


@runtime_checkable
class ProcessManagerServiceInterface(Protocol):
    """Interface for the process manager service."""

    def start_strategy(self) -> bool:
        """Start the Strategy process.

        Returns:
            bool: True if started successfully, False otherwise
        """
        ...

    def start_order_executor(self) -> bool:
        """Start the Order Executor process.

        Returns:
            bool: True if started successfully, False otherwise
        """
        ...


    def cleanup_processes(self) -> None:
        """Clean up all processes when exiting."""
        ...

    @property
    def strategy_process(self) -> Optional[subprocess.Popen]:
        """Get the strategy process.

        Returns:
            The strategy process if it exists, None otherwise
        """
        ...

    @property
    def order_executor_process(self) -> Optional[subprocess.Popen]:
        """Get the order executor process.

        Returns:
            The order executor process if it exists, None otherwise
        """
        ...

