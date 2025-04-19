from getpass import getpass

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.user_login_presenter import UserLoginPresenter
from src.app.cli_pfcf.views.user_login_view import UserLoginView
from src.infrastructure.repositories.user_in_memory_repository import UserInMemoryRepository
from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.user_login_dtos import UserLoginInputDto
from src.interactor.use_cases.user_login import UserLoginUseCase


class UserLoginController(CliMemoryControllerInterface):
    """ User login controller
    """

    def __init__(self, service_container: ServiceContainer):
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository

    def _get_user_info(self) -> UserLoginInputDto:
        """ Get user information from input
        """
        account = input("Enter the account: ")
        password = getpass("Enter the password: ")
        is_production = input("Is this login for production?[y/n](blank for n): ")
        ip_address = self.config.EXCHANGE_PROD_URL if is_production == "y" else self.config.EXCHANGE_TEST_URL
        return UserLoginInputDto(account, password, ip_address)

    def execute(self):
        """ Execute the user login controller
        """
        if self.session_repository.is_user_logged_in():
            self.logger.log_info("User already logged in")
            print("User already logged in")
            return
        repository = UserInMemoryRepository()
        presenter = UserLoginPresenter()
        input_dto = self._get_user_info()
        use_case = UserLoginUseCase(
            presenter, repository, self.config, self.logger, self.session_repository)
        result = use_case.execute(input_dto)
        view = UserLoginView()
        view.show(result)
