""" This module is responsible for user logout.
"""

from typing import Dict

from src.app.cli_pfcf.config import Config
from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto, UserLogoutOutputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.user_logout_presenter import UserLogoutPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.user_logout_validator import UserLogoutInputDtoValidator


class UserLogoutUseCase:
    """This class is responsible for user logout."""

    def __init__(
        self,
        presenter: UserLogoutPresenterInterface,
        config: Config,
        logger: LoggerInterface,
        session_manager: SessionRepositoryInterface,
    ):
        self.presenter = presenter
        self.config = config
        self.logger = logger
        self.session_manager = session_manager

    def execute(self, input_dto: UserLogoutInputDto) -> Dict:
        validator = UserLogoutInputDtoValidator(input_dto.to_dict())
        validator.validate()

        self.config.EXCHANGE_CLIENT.PFCLogout()

        self.session_manager.destroy_session()

        output_dto = UserLogoutOutputDto(account=input_dto.account, is_success=True)
        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info("User logout successfully")
        return presenter_response
