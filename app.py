"""Main application entry point for futures-trading-machine with DLL Gateway.

This module initializes the components, starts the DLL Gateway Server,
and runs the CLI process handler with centralized DLL access.
"""

import atexit
from pathlib import Path

from src.app.cli_pfcf.cli_pfcf_process_handler import CliMemoryProcessHandler
from src.app.cli_pfcf.config import Config
from src.app.cli_pfcf.controllers.create_condition_controller import CreateConditionController
from src.app.cli_pfcf.controllers.exit_controller import ExitController
from src.app.cli_pfcf.controllers.register_item_controller import RegisterItemController
from src.app.cli_pfcf.controllers.select_order_account_controller import (
    SelectOrderAccountController,
)
from src.app.cli_pfcf.controllers.send_market_order_controller import SendMarketOrderController
from src.app.cli_pfcf.controllers.show_futures_controller import ShowFuturesController
from src.app.cli_pfcf.controllers.all_in_one_controller import AllInOneController
from src.app.cli_pfcf.controllers.user_login_controller import UserLoginController
from src.app.cli_pfcf.controllers.user_logout_controller import UserLogoutController
from src.infrastructure.loggers.logger_default import LoggerDefault
from src.infrastructure.repositories.condition_json_file_repository import (
    ConditionJsonFileRepository,
)
from src.infrastructure.repositories.session_json_file_repository import SessionJsonFileRepository
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.pfcf_client.api import PFCFApi
from src.app.cli_pfcf.controllers.get_position_controller import GetPositionController
from src.infrastructure.services.dll_gateway_server import DllGatewayServer


# Global DLL Gateway Server instance for cleanup
_dll_gateway_server = None


def _setup_dll_gateway(exchange_api: PFCFApi, logger: LoggerDefault, config: Config) -> bool:
    """Setup and start DLL Gateway Server.
    
    Args:
        exchange_api: The exchange API client instance.
        logger: Logger for recording events.
        
    Returns:
        bool: True if gateway started successfully, False otherwise.
    """
    global _dll_gateway_server
    
    try:
        logger.log_info("Starting DLL Gateway Server...")
        
        _dll_gateway_server = DllGatewayServer(
            exchange_client=exchange_api,
            logger=logger,
            bind_address=config.DLL_GATEWAY_BIND_ADDRESS,
            request_timeout_ms=config.DLL_GATEWAY_REQUEST_TIMEOUT_MS,
        )
        
        if _dll_gateway_server.start():
            logger.log_info(f"DLL Gateway Server started successfully on {config.DLL_GATEWAY_BIND_ADDRESS}")
            
            # Register cleanup handler for graceful shutdown
            atexit.register(_cleanup_gateway)
            return True
        else:
            logger.log_error("Failed to start DLL Gateway Server")
            return False
            
    except Exception as e:
        logger.log_error(f"Error setting up DLL Gateway: {e}")
        return False


def _cleanup_gateway() -> None:
    """Cleanup DLL Gateway Server resources."""
    global _dll_gateway_server
    
    if _dll_gateway_server:
        try:
            print("\nShutting down DLL Gateway Server...")
            _dll_gateway_server.stop()
        except Exception as e:
            print(f"Error during DLL Gateway cleanup: {e}")


def main():
    """Main application entry point with DLL Gateway integration."""
    try:
        # Ensure the PID directory exists using pathlib for clarity
        pid_dir: Path = Path(__file__).resolve().parent / "tmp" / "pids"
        pid_dir.mkdir(parents=True, exist_ok=True)

        exchange_api = PFCFApi()
        config = Config(exchange_api)
        logger_default = LoggerDefault()
        session_repository = SessionJsonFileRepository(config.DEFAULT_SESSION_TIMEOUT)
        condition_repository = ConditionJsonFileRepository()

        # Setup DLL Gateway Server
        print("Initializing Auto Futures Trading Machine with DLL Gateway...")
        if not _setup_dll_gateway(exchange_api, logger_default, config):
            print("ERROR: Failed to start DLL Gateway Server")
            print("The application cannot run without the gateway service.")
            return

        print(f"✓ DLL Gateway Server: Running on {config.DLL_GATEWAY_CONNECT_ADDRESS}")
        print("✓ Exchange API: Centralized access through gateway")
        print("✓ Multi-process support: Enhanced security and stability")

        # Create service container
        service_container = ServiceContainer(
            logger=logger_default,
            config=config,
            session_repository=session_repository,
            condition_repository=condition_repository,
        )

        # Initialize CLI process handler
        process = CliMemoryProcessHandler(service_container)

        # Add main options
        process.add_option("0", ExitController())
        process.add_option("1", UserLoginController(service_container))
        process.add_option("2", UserLogoutController(service_container), "protected")
        process.add_option("3", RegisterItemController(service_container), "protected")
        process.add_option("4", CreateConditionController(service_container), "protected")
        process.add_option("5", SelectOrderAccountController(service_container), "protected")
        process.add_option("6", SendMarketOrderController(service_container), "protected")
        process.add_option("7", ShowFuturesController(service_container), "protected")
        process.add_option("8", GetPositionController(service_container), "protected")

        # Add all-in-one controller (option 10) - now uses Gateway architecture
        process.add_option("10", AllInOneController(service_container), "protected")

        print("\nIMPORTANT: AllInOneController (option 10) now uses Gateway architecture")
        print("All processes will communicate through the centralized DLL Gateway.")

        # Execute CLI process
        process.execute()
        
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        _cleanup_gateway()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated")
