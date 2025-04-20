from src.app.cli_pfcf.config import Config
from src.interactor.dtos.show_futures_dtos import ShowFuturesInputDto, ShowFuturesOutputDto
from src.interactor.interfaces.presenters.show_futures_presenter import (
    ShowFuturesPresenterInterface,
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


class ShowFuturesUseCase:
    """Use case for showing futures data"""

    def __init__(
        self,
        presenter: ShowFuturesPresenterInterface,
        config: Config,
        logger: LoggerInterface,
        session_repository: SessionRepositoryInterface,
    ):
        self.presenter = presenter
        self.config = config
        self.logger = logger
        self.session_repository = session_repository

    def execute(self, input_dto: ShowFuturesInputDto) -> ShowFuturesOutputDto:
        """Execute the use case"""
        try:
            if not self.session_repository.is_user_logged_in():
                return self.presenter.present_error("User not logged in")

            # Get futures data using PFC API
            api = self.config.EXCHANGE_CLIENT

            # If futures_code is specified, use it; otherwise, get all futures data
            futures_code = input_dto.futures_code if input_dto.futures_code else "ALL"

            print("futures_code", futures_code)

            self.logger.log_info(f"Getting futures data for code: {futures_code}")

            if futures_code == "ALL":
                data = api.PFCGetFutureData("")
            else:
                # Get data for specific futures code
                data = api.PFCGetFutureData(futures_code)
            return self.presenter.present_futures_data(data)

        except Exception as e:
            self.logger.log_error(f"Error in ShowFuturesUseCase: {str(e)}")
            return self.presenter.present_error(str(e))
