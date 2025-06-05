"""Main application entry point for futures-trading-machine.

This module initializes the components and starts the CLI process handler.
"""

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


def main():
    """Main application entry point."""
    # Ensure the PID directory exists using pathlib for clarity
    pid_dir: Path = Path(__file__).resolve().parent / "tmp" / "pids"
    pid_dir.mkdir(parents=True, exist_ok=True)

    exchange_api = PFCFApi()
    config = Config(exchange_api)
    logger_default = LoggerDefault()
    session_repository = SessionJsonFileRepository(config.DEFAULT_SESSION_TIMEOUT)
    condition_repository = ConditionJsonFileRepository()

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

    # Add all-in-one controller (option 10)
    process.add_option("10", AllInOneController(service_container), "protected")

    # Execute CLI process
    process.execute()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated")
