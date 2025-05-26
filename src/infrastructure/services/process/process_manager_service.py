"""Service for managing system processes.

This service provides functionality to start, stop, and monitor system processes
for various trading system components.
"""

# Standard library imports
import sys
import time
import subprocess
import threading
from pathlib import Path
from typing import Optional, Callable

from src.app.cli_pfcf.config import Config
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.process_manager_service_interface import (
    ProcessManagerServiceInterface,
)


class ProcessManagerService(ProcessManagerServiceInterface):
    """Service for managing system processes including strategy and order executor."""

    def __init__(self, config: Config, logger: LoggerInterface):
        """Initialize the process manager service.

        Args:
            config: Application configuration
            logger: Logger for recording events
        """
        self.config = config
        self.logger = logger

        # ------------------------------------------------------------------
        # Path configuration using pathlib for better readability & safety
        # ------------------------------------------------------------------
        # ``Path.parents[4]`` = project_root/src/../../.. -> project_root
        self.project_root: Path = Path(__file__).resolve().parents[4]

        # Paths to standalone process scripts
        self.strategy_script_path: Path = self.project_root / "run_strategy.py"
        self.order_executor_script_path: Path = self.project_root / "run_order_executor.py"

        # Directory for PID files
        self.pid_dir: Path = self.project_root / "tmp" / "pids"
        self.pid_dir.mkdir(parents=True, exist_ok=True)

        # Store process handles
        self._strategy_process: Optional[subprocess.Popen] = None
        self._order_executor_process: Optional[subprocess.Popen] = None
        self._gateway_thread: Optional[threading.Thread] = None
        self._gateway_running = False

    def start_strategy(self) -> bool:
        """Start the Strategy process.

        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.logger.log_info("Starting Strategy process...")

            # Get ZMQ addresses from config
            tick_sub_address = self.config.ZMQ_TICK_SUB_CONNECT_ADDRESS
            signal_push_address = self.config.ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS

            # Launch the process
            self._strategy_process = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    str(self.strategy_script_path),
                    "--tick-address",
                    tick_sub_address,
                    "--signal-address",
                    signal_push_address,
                ]
            )

            # Verify process started
            if self._strategy_process.poll() is None:
                self.logger.log_info(
                    f"Strategy process started with PID {self._strategy_process.pid}"
                )

                # Save PID for future reference
                self._save_pid("strategy", self._strategy_process.pid)
                return True
            else:
                self.logger.log_error("Strategy process failed to start")
                return False

        except Exception as e:
            self.logger.log_error(f"Failed to start Strategy process: {str(e)}")
            return False

    def start_order_executor(self) -> bool:
        """Start the Order Executor process.

        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.logger.log_info("Starting Order Executor process...")

            # Get ZMQ addresses from config
            signal_pull_address = self.config.ZMQ_SIGNAL_PULL_ADDRESS

            # Launch the process
            self._order_executor_process = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    str(self.order_executor_script_path),
                    "--signal-address",
                    signal_pull_address,
                ]
            )

            # Verify process started
            if self._order_executor_process.poll() is None:
                self.logger.log_info(
                    f"Order Executor process started with PID {self._order_executor_process.pid}"
                )

                # Save PID for future reference
                self._save_pid("order_executor", self._order_executor_process.pid)
                return True
            else:
                self.logger.log_error("Order Executor process failed to start")
                return False

        except Exception as e:
            self.logger.log_error(f"Failed to start Order Executor process: {str(e)}")
            return False

    def start_gateway_thread(self, gateway_runner: Callable) -> bool:
        """Start the Gateway in a separate thread.

        Args:
            gateway_runner: A callable that will run the gateway when executed

        Returns:
            bool: True if thread started successfully, False otherwise
        """
        try:
            self.logger.log_info("Starting Gateway in a background thread...")

            # Define thread target function to run gateway
            def run_gateway():
                try:
                    self._gateway_running = True
                    gateway_runner()
                except Exception as e:
                    self.logger.log_error(f"Gateway thread error: {str(e)}")
                finally:
                    self._gateway_running = False

            # Create and start the thread
            self._gateway_thread = threading.Thread(
                target=run_gateway,
                daemon=True,  # Use daemon thread to ensure it exits when main program exits
            )

            self._gateway_thread.start()

            # A brief pause to allow initialization to start
            time.sleep(2)

            if self._gateway_thread.is_alive():
                self.logger.log_info("Gateway thread started successfully")
                return True
            else:
                self.logger.log_error("Gateway thread failed to start")
                return False

        except Exception as e:
            self.logger.log_error(f"Failed to start Gateway thread: {str(e)}")
            return False

    def cleanup_processes(self) -> None:
        """Clean up all processes when exiting."""
        self.logger.log_info("Cleaning up trading system processes...")

        # Stop Strategy process
        if self._strategy_process and self._strategy_process.poll() is None:
            self.logger.log_info("Stopping Strategy process...")
            self._strategy_process.terminate()

            # Give it a moment to terminate gracefully
            time.sleep(0.5)

            if self._strategy_process.poll() is None:
                self.logger.log_info("Force killing Strategy process...")
                self._strategy_process.kill()

        # Stop Order Executor process
        if self._order_executor_process and self._order_executor_process.poll() is None:
            self.logger.log_info("Stopping Order Executor process...")
            self._order_executor_process.terminate()

            # Give it a moment to terminate gracefully
            time.sleep(0.5)

            if self._order_executor_process.poll() is None:
                self.logger.log_info("Force killing Order Executor process...")
                self._order_executor_process.kill()

        # Gateway is handled by the thread daemon attribute
        if self._gateway_thread and self._gateway_thread.is_alive():
            self.logger.log_info("Gateway thread will terminate when main application exits")

        # Clean up PID files
        self._cleanup_pid_files()

        self.logger.log_info("All processes cleaned up.")

    def _save_pid(self, process_name: str, pid: int) -> None:
        """Save process ID to a file for future reference.

        Args:
            process_name: Name of the process (for the filename)
            pid: Process ID to save
        """
        try:
            pid_file: Path = self.pid_dir / f"{process_name}.pid"
            pid_file.write_text(str(pid))
        except Exception as e:
            self.logger.log_warning(f"Failed to save PID file for {process_name}: {str(e)}")

    def _cleanup_pid_files(self) -> None:
        """Remove all PID files."""
        try:
            for file_path in self.pid_dir.glob("*.pid"):
                file_path.unlink(missing_ok=True)
        except Exception as e:
            self.logger.log_warning(f"Failed to clean up PID files: {str(e)}")

    @property
    def strategy_process(self) -> Optional[subprocess.Popen]:
        """Get the strategy process.

        Returns:
            The strategy process if it exists, None otherwise
        """
        return self._strategy_process

    @property
    def order_executor_process(self) -> Optional[subprocess.Popen]:
        """Get the order executor process.

        Returns:
            The order executor process if it exists, None otherwise
        """
        return self._order_executor_process

    @property
    def gateway_thread(self) -> Optional[threading.Thread]:
        """Get the gateway thread.

        Returns:
            The gateway thread if it exists, None otherwise
        """
        return self._gateway_thread

    @property
    def gateway_running(self) -> bool:
        """Check if the gateway is running.

        Returns:
            True if the gateway is running, False otherwise
        """
        return self._gateway_running
