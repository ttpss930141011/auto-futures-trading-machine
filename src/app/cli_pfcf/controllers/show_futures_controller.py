from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.show_futures_presenter import ShowFuturesPresenter
from src.app.cli_pfcf.views.show_futures_view import ShowFuturesView
from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.show_futures_dtos import ShowFuturesInputDto
from src.interactor.use_cases.show_futures import ShowFuturesUseCase


class ShowFuturesController(CliMemoryControllerInterface):
    """ Controller to display all futures data
    """

    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository

    def _get_user_info(self) -> ShowFuturesInputDto:
        account = self.session_repository.get_current_user()
        # Optional: Allows user to filter by futures code (e.g., TXF)
        futures_code = input("Enter futures code (leave empty for all): ")
        return ShowFuturesInputDto(account, futures_code)

    def execute(self):
        """ Execute and show all futures data
        """
        if self.session_repository.is_user_logged_in() is False:
            self.logger.log_info("User not logged in")
            return
            
        presenter = ShowFuturesPresenter()
        input_dto = self._get_user_info()
        use_case = ShowFuturesUseCase(presenter, self.service_container)
        result = use_case.execute(input_dto)
        view = ShowFuturesView()
        view.show(result) 