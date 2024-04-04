from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.select_order_account_presenter import SelectOrderAccountPresenter
from src.app.cli_pfcf.views.select_order_account_view import SelectOrderAccountView
from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountInputDto
from src.interactor.use_cases.select_order_account import SelectOrderAccountUseCase


class SelectOrderAccountController(CliMemoryControllerInterface):
    """ User login controller
    """

    def __init__(self, service_container: ServiceContainer):
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository

    def _get_user_input(self) -> SelectOrderAccountInputDto:
        account_set = self.config.EXCHANGE_CLIENT.UserOrderSet
        print("\nSelect the order account:")
        for account in account_set:
            print(f"{account_set.index(account) + 1}. {account}")
        account_number = input("\nEnter the account number: ")
        index = int(account_number) - 1
        order_account = account_set[index]
        return SelectOrderAccountInputDto(index=index, order_account=order_account)

    def execute(self):
        """ Execute the select order account controller
        """
        if not self.session_repository.is_user_logged_in():
            self.logger.log_info("User not login")
            return

        presenter = SelectOrderAccountPresenter()
        input_dto = self._get_user_input()
        use_case = SelectOrderAccountUseCase(presenter, self.config, self.logger, self.session_repository)
        result = use_case.execute(input_dto)
        view = SelectOrderAccountView()
        view.show(result)
