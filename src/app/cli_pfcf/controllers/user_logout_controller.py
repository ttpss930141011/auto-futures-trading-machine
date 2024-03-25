from typing import Type

from src.app.cli_pfcf.config import Config
from src.app.cli_pfcf.interfaces.cli_memory_controller_interface \
    import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.user_logout_presenter import UserLogoutPresenter
from src.app.cli_pfcf.views.user_logout_view import UserLogoutView
from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.session_manager.session_manager import SessionManagerInterface
from src.interactor.use_cases.user_logout import UserLogoutUseCase


class UserLogoutController(CliMemoryControllerInterface):
    """ User logout controller
    """

    def __init__(self, logger: LoggerInterface, config: Type[Config], session_manager: SessionManagerInterface):
        self.logger = logger
        self.config = config
        self.session_manager = session_manager

    def _get_user_info(self) -> UserLogoutInputDto:
        account = self.session_manager.get_current_user()
        return UserLogoutInputDto(account)

    def execute(self):
        """ Execute the user logout controller
        """
        if not self.session_manager.is_user_logged_in():
            print("User not logged in")
            return
        # repository = UserInMemoryRepository()
        presenter = UserLogoutPresenter()
        input_dto = self._get_user_info()
        use_case = UserLogoutUseCase(presenter, self.config, self.logger, self.session_manager)
        result = use_case.execute(input_dto)
        view = UserLogoutView()
        view.show(result)
