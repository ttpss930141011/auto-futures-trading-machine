"""Main application entry point for futures-trading-machine.

This module initializes the components and starts the CLI process handler.
"""

import os

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
from src.infrastructure.repositories.condition_in_memory_repository import (
    ConditionInMemoryRepository,
)
from src.infrastructure.repositories.session_in_memory_repository import SessionInMemoryRepository
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.pfcf_client.api import PFCFApi


def main():
    """Main application entry point."""
    # Create tmp/pids directory if it doesn't exist
    os.makedirs(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp", "pids"), exist_ok=True
    )

    exchange_api = PFCFApi()
    config = Config(exchange_api)
    logger_default = LoggerDefault()
    session_repository = SessionInMemoryRepository(config.DEFAULT_SESSION_TIMEOUT)
    condition_repository = ConditionInMemoryRepository()

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

    # Add all-in-one controller (option 10)
    process.add_option("10", AllInOneController(service_container), "protected")

    # Execute CLI process
    process.execute()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated")
