"""CLI Application for the futures trading machine.

This module provides the CLIApplication class which handles the
command-line interface and user interactions.
"""

import atexit
from typing import Optional

from src.app.cli_pfcf.cli_pfcf_process_handler import CliMemoryProcessHandler
from src.app.cli_pfcf.controllers.all_in_one_controller import AllInOneController
from src.app.cli_pfcf.controllers.create_condition_controller import CreateConditionController
from src.app.cli_pfcf.controllers.exit_controller import ExitController
from src.app.cli_pfcf.controllers.get_position_controller import GetPositionController
from src.app.cli_pfcf.controllers.register_item_controller import RegisterItemController
from src.app.cli_pfcf.controllers.select_order_account_controller import (
    SelectOrderAccountController,
)
from src.app.cli_pfcf.controllers.send_market_order_controller import SendMarketOrderController
from src.app.cli_pfcf.controllers.show_futures_controller import ShowFuturesController
from src.app.cli_pfcf.controllers.user_login_controller import UserLoginController
from src.app.cli_pfcf.controllers.user_logout_controller import UserLogoutController
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.services.system_manager import SystemManager


class CLIApplication:
    """CLI Application for user interaction.

    This class follows the Single Responsibility Principle by focusing
    solely on CLI interaction and controller management.
    """

    def __init__(self, system_manager: SystemManager, service_container: ServiceContainer) -> None:
        """Initialize the CLI application.

        Args:
            system_manager: System manager for infrastructure control
            service_container: Container with all services and dependencies
        """
        self._system_manager = system_manager
        self._service_container = service_container
        self._process_handler: Optional[CliMemoryProcessHandler] = None

        # Register cleanup on exit
        atexit.register(self._cleanup)

    def run(self) -> None:
        """Run the CLI application."""
        try:
            # Display startup information
            self._display_startup_info()

            # Initialize CLI process handler
            self._process_handler = self._create_process_handler()

            # Execute CLI process
            self._process_handler.execute()

        except KeyboardInterrupt:
            print("\nProgram terminated by user")
        except Exception as e:
            print(f"\nERROR: {e}")
        finally:
            self._cleanup()

    def _create_process_handler(self) -> CliMemoryProcessHandler:
        """Create and configure the CLI process handler.

        Returns:
            Configured CliMemoryProcessHandler instance
        """
        process_handler = CliMemoryProcessHandler(self._service_container)

        # Add main options
        process_handler.add_option("0", ExitController())
        process_handler.add_option("1", UserLoginController(self._service_container))
        process_handler.add_option("2", UserLogoutController(self._service_container), "protected")
        process_handler.add_option(
            "3", RegisterItemController(self._service_container), "protected"
        )
        process_handler.add_option(
            "4", CreateConditionController(self._service_container), "protected"
        )
        process_handler.add_option(
            "5", SelectOrderAccountController(self._service_container), "protected"
        )
        process_handler.add_option(
            "6", SendMarketOrderController(self._service_container), "protected"
        )
        process_handler.add_option("7", ShowFuturesController(self._service_container), "protected")
        process_handler.add_option("8", GetPositionController(self._service_container), "protected")

        # Add all-in-one controller with system manager
        all_in_one_controller = AllInOneController(self._service_container, self._system_manager)
        process_handler.add_option("10", all_in_one_controller, "protected")

        return process_handler

    def _display_startup_info(self) -> None:
        """Display startup information to the user."""
        print("Initializing Auto Futures Trading Machine with DLL Gateway...")
        print(
            f"✓ DLL Gateway Server: Running on {self._service_container.config.DLL_GATEWAY_CONNECT_ADDRESS}"
        )
        print("✓ Exchange API: Centralized access through gateway")
        print("✓ Multi-process support: Enhanced security and stability")
        print("\nIMPORTANT: AllInOneController (option 10) now uses Gateway architecture")
        print("All processes will communicate through the centralized DLL Gateway.")

    def _cleanup(self) -> None:
        """Cleanup resources on application exit."""
        try:
            print("\nShutting down application...")
            self._system_manager.stop_trading_system()
        except Exception as e:
            print(f"Error during cleanup: {e}")
