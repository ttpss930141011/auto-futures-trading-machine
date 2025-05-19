"""Process Manager Service Interface.

This module defines the interface for the process manager service.
"""

from typing import Protocol, Optional, Callable, runtime_checkable
import subprocess
import threading


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
        
    def start_gateway_thread(self, gateway_runner: Callable) -> bool:
        """Start the Gateway in a separate thread.

        Args:
            gateway_runner: A callable that will run the gateway when executed

        Returns:
            bool: True if thread started successfully, False otherwise
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
        
    @property
    def gateway_thread(self) -> Optional[threading.Thread]:
        """Get the gateway thread.

        Returns:
            The gateway thread if it exists, None otherwise
        """
        ...
        
    @property
    def gateway_running(self) -> bool:
        """Check if the gateway is running.

        Returns:
            True if the gateway is running, False otherwise
        """
        ...