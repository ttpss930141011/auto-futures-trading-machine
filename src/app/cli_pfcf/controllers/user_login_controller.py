from typing import Type

from config import Config
from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.user_login_presenter import UserLoginPresenter
from src.app.cli_pfcf.views.user_login_view import UserLoginView
from src.infrastructure.repositories.user_in_memory_repository import UserInMemoryRepository
from src.interactor.dtos.user_login_dtos import UserLoginInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.session_manager.session_manager import SessionManagerInterface
from src.interactor.use_cases.user_login import UserLoginUseCase


class UserLoginController(CliMemoryControllerInterface):
    """ User login controller
    """

    def __init__(self, logger: LoggerInterface, config: Type[Config], session_manager: SessionManagerInterface):
        self.logger = logger
        self.config = config
        self.session_manager = session_manager

    def _get_user_info(self) -> UserLoginInputDto:
        account = input("Enter the account: ")
        password = input("Enter the password: ")
        is_production = input("Is this login for production?[y/n](blank for n): ")
        ip_address = self.config.DEALER_PROD_URL if is_production == "y" else self.config.DEALER_TEST_URL

        return UserLoginInputDto(account, password, ip_address)

    def execute(self):
        """ Execute the user login controller
        """
        if self.session_manager.is_user_logged_in():
            print("User already logged in")
            return
        repository = UserInMemoryRepository()
        presenter = UserLoginPresenter()
        input_dto = self._get_user_info()
        use_case = UserLoginUseCase(
            presenter, repository, self.config, self.logger, self.session_manager)
        result = use_case.execute(input_dto)
        view = UserLoginView()
        view.show(result)
