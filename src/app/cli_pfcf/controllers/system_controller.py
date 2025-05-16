"""System Controller for managing all processes of the futures trading system.


This controller handles launching, monitoring, and stopping all components of the trading system,

including the Gateway, Strategy, and Order Executor processes.
"""

import os
import sys
import time
import signal

import subprocess

from typing import Dict, List, Optional


from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface

from src.infrastructure.services.service_container import ServiceContainer

from src.infrastructure.services.status_checker import StatusChecker
from src.interactor.use_cases.application_startup_status import ApplicationStartupStatusUseCase


class SystemController(CliMemoryControllerInterface):
    """Controller for managing the complete trading system lifecycle."""

    def __init__(self, service_container: ServiceContainer):
        """Initialize the system controller.


        Args:

            service_container: Container with all services and dependencies
        """

        self.service_container = service_container

        self.logger = service_container.logger

        self.config = service_container.config

        self.session_repository = service_container.session_repository

        self.status_checker = StatusChecker(service_container)

        # Store process handles

        self.gateway_process: Optional[subprocess.Popen] = None

        self.strategy_process: Optional[subprocess.Popen] = None

        self.order_executor_process: Optional[subprocess.Popen] = None

        # Keep track of running state

        self.running = False

        # System components paths relative to project root

        self.project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )

        self.gateway_script_path = os.path.join(
            self.project_root, "src", "app", "gateway_runner.py"
        )

        self.strategy_script_path = os.path.join(self.project_root, "run_strategy.py")

        self.order_executor_script_path = os.path.join(self.project_root, "run_order_executor.py")

        # PID file location for tracking processes

        self.pid_dir = os.path.join(self.project_root, "tmp", "pids")

        os.makedirs(self.pid_dir, exist_ok=True)

    def execute(self) -> None:
        """Execute the system controller, managing all trading system processes."""

        try:

            # Check if user is logged in

            if not self.session_repository.is_user_logged_in():

                self.logger.log_info("User not logged in")

                print("Please login first (option 1)")
                return

            # Create and execute use case for status checks

            start_app_use_case = ApplicationStartupStatusUseCase(
                logger=self.logger, status_checker=self.status_checker
            )

            status_summary = start_app_use_case.execute()

            # Display status to user

            self._display_status_summary(status_summary)

            # Check if we can proceed

            if not self._can_proceed(status_summary):

                self.logger.log_warning(
                    "Prerequisites not met. Please complete the setup before starting."
                )
                return

            # Show menu options for system management

            self._show_system_menu()

        except Exception as e:

            self.logger.log_error(f"System controller error: {str(e)}")

            print(f"\nERROR: System controller failed: {str(e)}")

        finally:

            # This ensures proper cleanup if needed

            if self.running:

                self._stop_all_processes()

    def _show_system_menu(self) -> None:
        """Display system management menu and handle user input."""

        menu_running = True

        while menu_running:

            print("\n=== Trading System Management ===")

            print("1. Start all components (Gateway, Strategy, Order Executor)")

            print("2. Start Gateway only")

            print("3. Start Strategy only")

            print("4. Start Order Executor only")

            print("5. Stop all components")

            print("6. Check system status")

            print("0. Exit system controller")

            try:

                choice = input("\nEnter your choice (0-6): ")

                if choice == "0":

                    menu_running = False

                    print("Exiting system controller...")

                elif choice == "1":

                    self._start_all_processes()

                elif choice == "2":

                    self._start_gateway()

                elif choice == "3":

                    self._start_strategy()

                elif choice == "4":

                    self._start_order_executor()

                elif choice == "5":

                    self._stop_all_processes()

                elif choice == "6":

                    self._check_system_status()

                else:

                    print("Invalid choice. Please try again.")

            except KeyboardInterrupt:

                print("\nOperation cancelled.")
                continue

            except Exception as e:

                self.logger.log_error(f"Error in system menu: {str(e)}")

                print(f"Error in system menu: {str(e)}")

    def _start_all_processes(self) -> None:
        """Start all system components in the correct order."""

        print("\nStarting all trading system components...")

        # First stop any running processes

        self._stop_all_processes()

        # Start Gateway

        success_gateway = self._start_gateway()

        if not success_gateway:

            print("Failed to start Gateway. Aborting system startup.")
            return

        # Wait a moment for Gateway to initialize

        time.sleep(2)

        # Start Strategy

        success_strategy = self._start_strategy()

        if not success_strategy:

            print("Failed to start Strategy process.")

            # We continue anyway to allow partial system operation

        # Start Order Executor

        success_executor = self._start_order_executor()

        if not success_executor:

            print("Failed to start Order Executor process.")

            # We continue anyway to allow partial system operation

        self.running = True

        print("\nAll available system components started.")

        print("Use option 6 to check system status or option 5 to stop all components.")

    def _start_gateway(self) -> bool:
        """Start the Gateway process.


        Returns:

            bool: True if started successfully, False otherwise
        """

        try:

            print("\nStarting Gateway process...")

            # For now we'll use the GatewayController from the main app

            # In a future implementation, create a standalone gateway_runner.py script

            print("Gateway must be started from the main menu (option 8)")

            print("Please run option 8 in the main menu after this controller exits")

            # Actual implementation would create a child process:

            # self.gateway_process = subprocess.Popen(

            #     [sys.executable, self.gateway_script_path],

            #     stdout=subprocess.PIPE,

            #     stderr=subprocess.PIPE,

            #     text=True

            # )

            return True

        except Exception as e:

            self.logger.log_error(f"Failed to start Gateway process: {str(e)}")

            print(f"ERROR: Failed to start Gateway process: {str(e)}")

            return False

    def _start_strategy(self) -> bool:
        """Start the Strategy process.


        Returns:

            bool: True if started successfully, False otherwise
        """

        try:

            print("\nStarting Strategy process...")

            # Get ZMQ addresses from config

            tick_sub_address = self.config.ZMQ_TICK_SUB_CONNECT_ADDRESS

            signal_push_address = self.config.ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS

            # Launch the process

            self.strategy_process = subprocess.Popen(
                [
                    sys.executable,
                    self.strategy_script_path,
                    "--tick-address",
                    tick_sub_address,
                    "--signal-address",
                    signal_push_address,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Verify process started

            if self.strategy_process.poll() is None:

                print(f"Strategy process started with PID {self.strategy_process.pid}")

                # Save PID for future reference

                self._save_pid("strategy", self.strategy_process.pid)

                return True

            else:

                print("Strategy process failed to start")

                return False

        except Exception as e:

            self.logger.log_error(f"Failed to start Strategy process: {str(e)}")

            print(f"ERROR: Failed to start Strategy process: {str(e)}")

            return False

    def _start_order_executor(self) -> bool:
        """Start the Order Executor process.


        Returns:

            bool: True if started successfully, False otherwise
        """

        try:

            print("\nStarting Order Executor process...")

            # Get ZMQ addresses from config

            signal_pull_address = self.config.ZMQ_SIGNAL_PULL_ADDRESS

            # Launch the process

            self.order_executor_process = subprocess.Popen(
                [
                    sys.executable,
                    self.order_executor_script_path,
                    "--signal-address",
                    signal_pull_address,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Verify process started

            if self.order_executor_process.poll() is None:

                print(f"Order Executor process started with PID {self.order_executor_process.pid}")

                # Save PID for future reference

                self._save_pid("order_executor", self.order_executor_process.pid)

                return True

            else:

                print("Order Executor process failed to start")

                return False

        except Exception as e:

            self.logger.log_error(f"Failed to start Order Executor process: {str(e)}")

            print(f"ERROR: Failed to start Order Executor process: {str(e)}")

            return False

    def _stop_all_processes(self) -> None:
        """Stop all running system components."""

        print("\nStopping all system components...")

        # Stop Strategy process

        if self.strategy_process and self.strategy_process.poll() is None:

            print("Stopping Strategy process...")

            self.strategy_process.terminate()

            # Give it a moment to terminate gracefully

            time.sleep(0.5)

            if self.strategy_process.poll() is None:

                print("Force killing Strategy process...")

                self.strategy_process.kill()

        # Stop Order Executor process

        if self.order_executor_process and self.order_executor_process.poll() is None:

            print("Stopping Order Executor process...")

            self.order_executor_process.terminate()

            # Give it a moment to terminate gracefully

            time.sleep(0.5)

            if self.order_executor_process.poll() is None:

                print("Force killing Order Executor process...")

                self.order_executor_process.kill()

        # Note: Gateway process should be stopped manually (option 8)

        print("NOTE: Gateway process must be stopped manually (Ctrl+C in its terminal)")

        # Clean up PID files

        self._cleanup_pid_files()

        self.running = False

        print("All managed processes stopped.")

    def _check_system_status(self) -> None:
        """Check and display the status of all system components."""

        print("\n=== System Status ===")

        # Check Gateway status

        print("Gateway: Running via menu option 8 (check manually)")

        # Check Strategy status

        strategy_running = False

        if self.strategy_process and self.strategy_process.poll() is None:

            strategy_running = True

        else:

            # Check if we have a PID file and if the process is still running

            pid = self._load_pid("strategy")

            if pid and self._is_process_running(pid):

                strategy_running = True

                # Update our reference

                self.strategy_process = self._get_process_by_pid(pid)

        print(f"Strategy: {'RUNNING' if strategy_running else 'STOPPED'}")

        # Check Order Executor status

        executor_running = False

        if self.order_executor_process and self.order_executor_process.poll() is None:

            executor_running = True

        else:

            # Check if we have a PID file and if the process is still running

            pid = self._load_pid("order_executor")

            if pid and self._is_process_running(pid):

                executor_running = True

                # Update our reference

                self.order_executor_process = self._get_process_by_pid(pid)

        print(f"Order Executor: {'RUNNING' if executor_running else 'STOPPED'}")

        print("=====================")

    def _display_status_summary(self, status_summary: Dict[str, bool]) -> None:
        """Display status summary to the user.


        Args:

            status_summary: Dictionary with status check results
        """

        print("\n=== System Status ===")

        print(f"User logged in: {'✓' if status_summary['logged_in'] else '✗'}")

        print(f"Item registered: {'✓' if status_summary['item_registered'] else '✗'}")

        print(f"Order account selected: {'✓' if status_summary['order_account_selected'] else '✗'}")

        print(f"Trading conditions defined: {'✓' if status_summary['has_conditions'] else '✗'}")

        print("=====================\n")

    def _can_proceed(self, status_summary: Dict[str, bool]) -> bool:
        """Check if all prerequisites are met to start the system.


        Args:

            status_summary: Dictionary with status check results


        Returns:

            True if all checks passed, False otherwise
        """

        return all(status_summary.values())

    def _save_pid(self, process_name: str, pid: int) -> None:
        """Save process ID to a file for future reference.


        Args:

            process_name: Name of the process (for the filename)

            pid: Process ID to save
        """

        try:

            pid_file = os.path.join(self.pid_dir, f"{process_name}.pid")

            with open(pid_file, "w") as f:

                f.write(str(pid))

        except Exception as e:

            self.logger.log_warning(f"Failed to save PID file for {process_name}: {str(e)}")

    def _load_pid(self, process_name: str) -> Optional[int]:
        """Load a process ID from file.


        Args:

            process_name: Name of the process (for the filename)


        Returns:

            Process ID if file exists, None otherwise
        """

        try:

            pid_file = os.path.join(self.pid_dir, f"{process_name}.pid")

            if os.path.exists(pid_file):

                with open(pid_file, "r") as f:

                    return int(f.read().strip())

            return None

        except Exception as e:

            self.logger.log_warning(f"Failed to load PID file for {process_name}: {str(e)}")

            return None

    def _cleanup_pid_files(self) -> None:
        """Remove all PID files."""

        try:

            for filename in os.listdir(self.pid_dir):

                if filename.endswith(".pid"):

                    os.remove(os.path.join(self.pid_dir, filename))

        except Exception as e:

            self.logger.log_warning(f"Failed to clean up PID files: {str(e)}")

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with the given PID is running.


        Args:

            pid: Process ID to check


        Returns:

            True if process is running, False otherwise
        """

        try:

            # This is platform-specific; on Windows we would use a different approach

            os.kill(pid, 0)

            return True

        except OSError:

            return False

        except Exception:

            return False

    def _get_process_by_pid(self, pid: int) -> Optional[subprocess.Popen]:
        """Get a Popen object for an existing process by PID.


        This is a limited implementation that doesn't capture stdout/stderr.


        Args:

            pid: Process ID


        Returns:

            Popen object or None if process not found
        """

        try:

            # We can't fully reconstruct a Popen object for existing processes

            # Just create a simple placeholder with minimal functionality

            process = subprocess.Popen(["echo", "dummy"])  # Create any process

            process.pid = pid  # Override the pid
            return process

        except Exception:

            return None


# Import here to avoid circular imports
