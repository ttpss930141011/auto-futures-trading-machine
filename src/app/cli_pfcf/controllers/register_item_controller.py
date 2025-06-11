from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.register_item_presenter import RegisterItemPresenter
from src.app.cli_pfcf.views.register_item_view import RegisterItemView
from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.register_item_dtos import RegisterItemInputDto
from src.interactor.use_cases.register_item import RegisterItemUseCase


class RegisterItemController(CliMemoryControllerInterface):
    """ User register item
    """

    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository

    def _get_user_info(self) -> RegisterItemInputDto:
        account = self.session_repository.get_current_user()
        item_code = input("Enter item code: ")
        return RegisterItemInputDto(account, item_code)

    def execute(self):
        """ Execute the user register item
        """
        if self.session_repository.is_user_logged_in() is False:
            self.logger.log_info("User not login")
            return
        presenter = RegisterItemPresenter()
        input_dto = self._get_user_info()
        use_case = RegisterItemUseCase(presenter, self.service_container)
        result = use_case.execute(input_dto)
        view = RegisterItemView()
        view.show(result)
