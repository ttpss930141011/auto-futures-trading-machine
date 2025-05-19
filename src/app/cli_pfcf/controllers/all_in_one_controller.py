"""All-in-One Controller for starting all trading system services at once.

This controller handles launching the Gateway, Strategy, and Order Executor processes
in a non-blocking way, allowing users to continue using the main menu.
"""

from typing import Dict

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.services.status_checker import StatusChecker
from src.infrastructure.services.gateway.port_checker_service import PortCheckerService
from src.infrastructure.services.gateway.gateway_initializer_service import GatewayInitializerService
from src.infrastructure.services.process.process_manager_service import ProcessManagerService
from src.interactor.use_cases.application_startup_status import ApplicationStartupStatusUseCase
from src.interactor.use_cases.start_strategy_use_case import StartStrategyUseCase
from src.interactor.use_cases.start_order_executor_use_case import StartOrderExecutorUseCase
from src.interactor.use_cases.run_gateway_use_case import RunGatewayUseCase


class AllInOneController(CliMemoryControllerInterface):
    """Controller for starting all trading system components at once."""

    def __init__(self, service_container: ServiceContainer) -> None:
        """Initialize the all-in-one controller.

        Args:
            service_container: Container with all services and dependencies
        """
        self.service_container = service_container
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository
        self.status_checker = StatusChecker(service_container)

        # Initialize services
        self.port_checker_service = PortCheckerService(self.config, self.logger)
        self.gateway_initializer_service = GatewayInitializerService(self.config, self.logger)
        self.process_manager_service = ProcessManagerService(self.config, self.logger)

        # Initialize use cases
        self.startup_status_use_case = ApplicationStartupStatusUseCase(
            logger=self.logger, status_checker=self.status_checker
        )
        
        self.run_gateway_use_case = RunGatewayUseCase(
            logger=self.logger,
            port_checker_service=self.port_checker_service,
            gateway_initializer_service=self.gateway_initializer_service,
            session_repository=self.session_repository
        )

        self.start_strategy_use_case = StartStrategyUseCase(
            logger=self.logger, 
            process_manager_service=self.process_manager_service
        )

        self.start_order_executor_use_case = StartOrderExecutorUseCase(
            logger=self.logger, 
            process_manager_service=self.process_manager_service
        )

    def execute(self) -> None:
        """Execute the all-in-one controller to start all system components."""
        try:
            # Check if user is logged in
            if not self.session_repository.is_user_logged_in():
                self.logger.log_info("User not logged in")
                print("Please login first (option 1)")
                return

            # Check application status directly
            status_summary = self.startup_status_use_case.execute()
            
            # Check if we can proceed
            if not all(status_summary.values()):
                self.logger.log_warning(
                    "Prerequisites not met. Please complete the setup before starting."
                )
                # Display status for user information
                self._display_status_summary(status_summary)
                return
            
            # Initialize results dictionary
            results = {
                "status_check": True,
                "gateway": False,
                "strategy": False,
                "order_executor": False
            }
            
            # Start Gateway in a thread
            print("\n=== Starting All Trading System Components ===")
            print("\nStarting Gateway thread...")
            gateway_success = self._start_gateway_thread()
            results["gateway"] = gateway_success
            
            if not gateway_success:
                self.logger.log_error("Failed to start Gateway thread. Aborting system startup.")
                self._display_startup_results(results)
                return
            
            # Wait for Gateway to initialize
            print("Waiting for Gateway to initialize...")
            import time
            time.sleep(3)
            
            # Start Strategy
            print("\nStarting Strategy process...")
            strategy_success = self.start_strategy_use_case.execute()
            results["strategy"] = strategy_success
            
            if not strategy_success:
                self.logger.log_warning("Failed to start Strategy process.")
                # We continue anyway to allow partial system operation
            
            # Start Order Executor
            print("\nStarting Order Executor process...")
            order_executor_success = self.start_order_executor_use_case.execute()
            results["order_executor"] = order_executor_success
            
            if not order_executor_success:
                self.logger.log_warning("Failed to start Order Executor process.")
                # We continue anyway to allow partial system operation
            
            # Show results to user
            self._display_startup_results(results)
            
            # Register cleanup handler
            import atexit
            atexit.register(self.process_manager_service.cleanup_processes)
            
            # Display additional information if all components started
            if all(results.values()):
                print("\nAll system components have been started.")
                print("You can continue using the main menu. The processes will run in the background.")
                print("The system will automatically clean up when you exit the application.")
            
        except Exception as e:
            self.logger.log_error(f"All-in-one controller error: {str(e)}")
            print(f"\nERROR: Failed to start system components: {str(e)}")
            self.process_manager_service.cleanup_processes()

    def _start_gateway_thread(self) -> bool:
        """Start the Gateway in a separate thread using RunGatewayUseCase.
        
        Returns:
            bool: True if gateway thread started successfully, False otherwise
        """
        # Create a function for the process manager to execute in a thread
        def gateway_runner():
            # Use threaded mode for the gateway
            self.run_gateway_use_case.execute(is_threaded_mode=True)
        
        # Use the process manager to start the gateway thread
        return self.process_manager_service.start_gateway_thread(gateway_runner)

    def _display_startup_results(self, results: Dict[str, bool]) -> None:
        """Display startup results to the user.

        Args:
            results: Dictionary with component names as keys and startup success as values
        """
        print("\n=== System Startup Results ===")
        print(f"Prerequisites check: {'✓' if results['status_check'] else '✗'}")
        print(f"Gateway: {'✓' if results['gateway'] else '✗'}")
        print(f"Strategy: {'✓' if results['strategy'] else '✗'}")
        print(f"Order Executor: {'✓' if results['order_executor'] else '✗'}")
        print("=============================\n")
        
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