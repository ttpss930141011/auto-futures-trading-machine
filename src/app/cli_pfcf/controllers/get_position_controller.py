"""
CLI controller for retrieving real-time positions.
"""

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.infrastructure.repositories.pfcf_position_repository import PFCFPositionRepository
from src.interactor.dtos.get_position_dtos import GetPositionInputDto
from src.interactor.use_cases.get_position_use_case import GetPositionUseCase
from src.app.cli_pfcf.presenters.get_position_presenter import GetPositionPresenter


class GetPositionController(CliMemoryControllerInterface):
    """Controller to fetch and display account positions."""

    def __init__(self, service_container):
        """Initialize the get position controller.
        
        Args:
            service_container: Provides shared services (logger, session_repository, exchange_api).
        """
        self.service_container = service_container
        self.logger = service_container.logger
        self.session_repository = service_container.session_repository

    def _get_user_input(self) -> GetPositionInputDto:
        """
        Prompt for customer account and product ID.

        Returns:
            GetPositionInputDto with user inputs.
        """
        order_account = self.session_repository.get_order_account()
        print(f"Account: {order_account}")
        product_id = input("Enter product id (leave blank for all): ")
        return GetPositionInputDto(order_account=order_account, product_id=product_id)

    def execute(self) -> None:
        """Execute the controller: run use case and print results."""
        if not self.session_repository.is_user_logged_in():
            self.logger.log_info("User not logged in")
            return

        # Prepare infrastructure and use case
        repository = PFCFPositionRepository(client=self.service_container.exchange_client)
        presenter = GetPositionPresenter()
        use_case = GetPositionUseCase(repository, presenter, self.logger)

        input_dto = self._get_user_input()
        result = use_case.execute(input_dto)

        # Display result directly
        print(result)
