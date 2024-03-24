from config import Config
from src.app.cli_pfcf.cli_pfcf_process_handler import CliMemoryProcessHandler
from src.app.cli_pfcf.controllers.exit_controller import ExitController
from src.app.cli_pfcf.controllers.user_login_controller import UserLoginController
from src.infrastructure.loggers.logger_default import LoggerDefault

if __name__ == "__main__":
    logger_default = LoggerDefault()
    process = CliMemoryProcessHandler(logger_default)
    process.add_option("0", ExitController())
    process.add_option("1", UserLoginController(logger_default, Config))
    process.execute()
