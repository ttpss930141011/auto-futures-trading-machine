from src.app.cli_pfcf.cli_pfcf_process_handler import CliMemoryProcessHandler
from src.app.cli_pfcf.config import Config
from src.app.cli_pfcf.controllers.exit_controller import ExitController
from src.app.cli_pfcf.controllers.user_login_controller import UserLoginController
from src.app.cli_pfcf.controllers.user_logout_controller import UserLogoutController
from src.infrastructure.loggers.logger_default import LoggerDefault
from src.infrastructure.session_manager.session_manager import SessionManager

if __name__ == "__main__":
    logger_default = LoggerDefault()
    session_manager = SessionManager(Config.DEFAULT_SESSION_TIMEOUT)
    process = CliMemoryProcessHandler(logger_default, session_manager)
    process.add_option("0", ExitController())
    process.add_option("1", UserLoginController(logger_default, Config, session_manager))
    process.add_option("2", UserLogoutController(logger_default, Config, session_manager), "protected")

    process.execute()
