"""All-in-One Controller for starting all trading system services at once.

This controller handles user interaction for starting the trading system
while delegating infrastructure management to the SystemManager.
"""

from typing import Dict, Optional

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.services.system_manager import SystemManager, ComponentStatus
from src.interactor.use_cases.application_startup_status import ApplicationStartupStatusUseCase


class AllInOneController(CliMemoryControllerInterface):
    """Controller for starting all trading system components at once.

    This class follows the Single Responsibility Principle by focusing
    on user interaction while delegating infrastructure management.
    """

    def __init__(self, service_container: ServiceContainer, system_manager: SystemManager) -> None:
        """Initialize the all-in-one controller.

        Args:
            service_container: Container with all services and dependencies
            system_manager: System manager for infrastructure control
        """
        self._service_container = service_container
        self._system_manager = system_manager
        self._logger = service_container.logger
        self._session_repository = service_container.session_repository

        # Initialize use case for status checking
        from src.infrastructure.services.status_checker import StatusChecker

        status_checker = StatusChecker(service_container)
        self._startup_status_use_case = ApplicationStartupStatusUseCase(
            logger=self._logger, status_checker=status_checker
        )

    def execute(self) -> None:
        """Execute the all-in-one controller to start all system components."""
        try:
            # Step 1: Validate prerequisites
            if not self._validate_prerequisites():
                return

            # Step 2: Start trading system through SystemManager
            print("\n=== Starting All Trading System Components ===")
            result = self._system_manager.start_trading_system()

            # Step 3: Display results
            self._display_startup_results(result)

            # Step 4: Show additional information if successful
            if result.success:
                self._display_success_message()
            else:
                self._display_error_message(result.error_message)

        except (RuntimeError, OSError, ValueError) as e:
            self._logger.log_error(f"All-in-one controller error: {str(e)}")
            print(f"\nERROR: Failed to start system components: {str(e)}")

    def _validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met.

        Returns:
            True if all prerequisites are met, False otherwise
        """
        # Check if user is logged in
        if not self._session_repository.is_user_logged_in():
            self._logger.log_info("User not logged in")
            print("Please login first (option 1)")
            return False

        # Check application status
        status_summary = self._startup_status_use_case.execute()

        # Check if we can proceed
        if not all(status_summary.values()):
            self._logger.log_warning(
                "Prerequisites not met. Please complete the setup before starting."
            )
            self._display_status_summary(status_summary)
            return False

        return True

    def _display_startup_results(self, result) -> None:
        """Display startup results to the user.

        Args:
            result: SystemStartupResult from SystemManager
        """
        print("\n=== System Startup Results ===")
        print(f"Overall Status: {'✓ Success' if result.success else '✗ Failed'}")
        print(f"Gateway: {self._format_component_status(result.gateway_status)}")
        print(f"Strategy: {self._format_component_status(result.strategy_status)}")
        print(f"Order Executor: {self._format_component_status(result.order_executor_status)}")
        print("=============================\n")

    def _format_component_status(self, status: ComponentStatus) -> str:
        """Format component status for display.

        Args:
            status: Component status enum

        Returns:
            Formatted status string
        """
        status_symbols = {
            ComponentStatus.RUNNING: "✓ Running",
            ComponentStatus.STOPPED: "✗ Stopped",
            ComponentStatus.ERROR: "✗ Error",
            ComponentStatus.STARTING: "⟳ Starting",
            ComponentStatus.STOPPING: "⟳ Stopping",
        }
        return status_symbols.get(status, str(status.value))

    def _display_status_summary(self, status_summary: Dict[str, bool]) -> None:
        """Display status summary to the user.

        Args:
            status_summary: Dictionary with status check results
        """
        print("\n=== System Prerequisites ===")
        print(f"User logged in: {'✓' if status_summary['logged_in'] else '✗'}")
        print(f"Item registered: {'✓' if status_summary['item_registered'] else '✗'}")
        print(f"Order account selected: {'✓' if status_summary['order_account_selected'] else '✗'}")
        print(f"Trading conditions defined: {'✓' if status_summary['has_conditions'] else '✗'}")
        print("===========================\n")

    def _display_success_message(self) -> None:
        """Display success message to the user."""
        print("\nAll system components have been started successfully.")
        print("You can continue using the main menu. The processes will run in the background.")
        print("The system will automatically clean up when you exit the application.")

    def _display_error_message(self, error_message: Optional[str]) -> None:
        """Display error message to the user.

        Args:
            error_message: Optional error message from system manager
        """
        print("\nFailed to start all system components.")
        if error_message:
            print(f"Error: {error_message}")
        print("Please check the logs for more details.")
