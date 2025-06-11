from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.show_futures_dtos import ShowFuturesInputDto, ShowFuturesOutputDto
from src.interactor.interfaces.presenters.show_futures_presenter import (
    ShowFuturesPresenterInterface,
)


class ShowFuturesUseCase:
    """Use case for showing futures data.

    This class handles the business logic for retrieving and displaying
    futures data from the exchange, including validation and error handling.
    """

    def __init__(
        self,
        presenter: ShowFuturesPresenterInterface,
        service_container: ServiceContainer,
    ) -> None:
        """Initialize the ShowFuturesUseCase.

        Args:
            presenter: The presenter interface for formatting output.
            service_container: Container providing access to all required services.
        """
        self.presenter = presenter
        self.service_container = service_container

    def execute(self, input_dto: ShowFuturesInputDto) -> ShowFuturesOutputDto:
        """Execute the show futures use case.

        Args:
            input_dto: The input data transfer object containing futures query details.

        Returns:
            ShowFuturesOutputDto: The formatted response containing futures data or error.
        """
        try:
            if not self.service_container.session_repository.is_user_logged_in():
                return self.presenter.present_error("User not logged in")

            # Get futures data using PFC API
            api = self.service_container.exchange_client

            # If futures_code is specified, use it; otherwise, get all futures data
            futures_code = input_dto.futures_code if input_dto.futures_code else "ALL"

            print("futures_code", futures_code)

            self.service_container.logger.log_info(f"Getting futures data for code: {futures_code}")

            if futures_code == "ALL":
                data = api.PFCGetFutureData("")
            else:
                # Get data for specific futures code
                data = api.PFCGetFutureData(futures_code)
            return self.presenter.present_futures_data(data)

        except Exception as e:
            self.service_container.logger.log_error(f"Error in ShowFuturesUseCase: {str(e)}")
            return self.presenter.present_error(str(e))
