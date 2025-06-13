from src.app.cli_pfcf.interfaces.cli_memory_controller_interface \
    import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.user_logout_presenter import UserLogoutPresenter
from src.app.cli_pfcf.views.user_logout_view import UserLogoutView
from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto
from src.interactor.use_cases.user_logout import UserLogoutUseCase


class UserLogoutController(CliMemoryControllerInterface):
    """ User logout controller
    """

    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository

    def _get_user_info(self) -> UserLogoutInputDto:
        account = self.session_repository.get_current_user()
        return UserLogoutInputDto(account)

    def execute(self):
        """ Execute the user logout controller
        """
        if not self.session_repository.is_user_logged_in():
            self.logger.log_info("User not login")
            return
        presenter = UserLogoutPresenter()
        input_dto = self._get_user_info()
        use_case = UserLogoutUseCase(presenter, self.service_container, self.logger, self.session_repository)
        result = use_case.execute(input_dto)
        view = UserLogoutView()
        view.show(result)
