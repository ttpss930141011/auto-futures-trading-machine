"""All-in-One Controller for starting all trading system services at once.


This controller handles launching the Gateway, Strategy, and Order Executor processes

in a non-blocking way, allowing users to continue using the main menu.
"""

import os

import sys

import time

import subprocess

import threading

from typing import Dict, Optional


from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface

from src.infrastructure.services.service_container import ServiceContainer

from src.infrastructure.services.status_checker import StatusChecker

from src.interactor.use_cases.application_startup_status import ApplicationStartupStatusUseCase


class AllInOneController(CliMemoryControllerInterface):
    """Controller for starting all trading system components at once."""

    def __init__(self, service_container: ServiceContainer):
        """Initialize the all-in-one controller.


        Args:

            service_container: Container with all services and dependencies
        """

        self.service_container = service_container

        self.logger = service_container.logger

        self.config = service_container.config

        self.session_repository = service_container.session_repository

        self.status_checker = StatusChecker(service_container)

        # Store process handles

        self.gateway_thread: Optional[threading.Thread] = None

        self.strategy_process: Optional[subprocess.Popen] = None

        self.order_executor_process: Optional[subprocess.Popen] = None

        # System components paths relative to project root

        self.project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )

        self.strategy_script_path = os.path.join(self.project_root, "run_strategy.py")

        self.order_executor_script_path = os.path.join(self.project_root, "run_order_executor.py")

        # PID file location for tracking processes

        self.pid_dir = os.path.join(self.project_root, "tmp", "pids")

        os.makedirs(self.pid_dir, exist_ok=True)

        # Create a flag to track if gateway is running

        self.gateway_running = False

    def execute(self) -> None:
        """Execute the all-in-one controller to start all system components."""

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

            # Start all components in the right order

            print("\n=== Starting All Trading System Components ===")

            # First start the Gateway in a separate thread

            success_gateway = self._start_gateway_thread()

            if not success_gateway:

                print("Failed to start Gateway thread. Aborting system startup.")
                return

            # Wait for Gateway to initialize

            print("Waiting for Gateway to initialize...")

            time.sleep(3)

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

            print("\nAll system components have been started.")

            print("You can continue using the main menu. The processes will run in the background.")

            print("The system will automatically clean up when you exit the application.")

            # Register shutdown handler to ensure cleanup

            import atexit

            atexit.register(self._cleanup_processes)

        except Exception as e:

            self.logger.log_error(f"All-in-one controller error: {str(e)}")

            print(f"\nERROR: Failed to start system components: {str(e)}")

            self._cleanup_processes()

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

    def _start_gateway_thread(self) -> bool:
        """Start the Gateway in a separate thread.


        Returns:

            bool: True if thread started successfully, False otherwise
        """

        try:

            print("\nStarting Gateway in a background thread...")

            # Import here to avoid circular imports

            from src.app.cli_pfcf.controllers.gateway_controller import GatewayController

            # Create a gateway controller with threaded mode enabled

            gateway_controller = GatewayController(self.service_container, is_threaded_mode=True)

            # Define thread target function to run gateway

            def run_gateway():

                try:

                    self.gateway_running = True

                    gateway_controller.execute()

                except Exception as e:

                    self.logger.log_error(f"Gateway thread error: {str(e)}")

                finally:

                    self.gateway_running = False

            # Create and start the thread

            self.gateway_thread = threading.Thread(
                target=run_gateway,
                daemon=True,  # Use daemon thread to ensure it exits when main program exits
            )

            self.gateway_thread.start()

            # A brief pause to allow initialization to start

            time.sleep(2)

            if self.gateway_thread.is_alive():

                print("Gateway thread started successfully")

                return True

            else:

                print("Gateway thread failed to start")

                return False

        except Exception as e:

            self.logger.log_error(f"Failed to start Gateway thread: {str(e)}")

            print(f"ERROR: Failed to start Gateway thread: {str(e)}")

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

    def _cleanup_processes(self) -> None:
        """Clean up all processes when exiting."""

        print("\nCleaning up trading system processes...")

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

        # Gateway is handled by the thread daemon attribute

        if self.gateway_thread and self.gateway_thread.is_alive():

            print("Gateway thread will terminate when main application exits")

        # Clean up PID files

        self._cleanup_pid_files()

        print("All processes cleaned up.")

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

    def _cleanup_pid_files(self) -> None:
        """Remove all PID files."""

        try:

            for filename in os.listdir(self.pid_dir):

                if filename.endswith(".pid"):

                    os.remove(os.path.join(self.pid_dir, filename))

        except Exception as e:

            self.logger.log_warning(f"Failed to clean up PID files: {str(e)}")
