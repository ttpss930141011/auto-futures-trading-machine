""" This module is responsible for user logout.
"""
from datetime import datetime
from typing import Dict, Type

from src.app.cli_pfcf.config import Config
from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto, UserLogoutOutputDto
from src.interactor.errors.error_classes import LogoutFailedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.user_logout_presenter import UserLogoutPresenterInterface
from src.interactor.interfaces.session_manager.session_manager import SessionManagerInterface
from src.interactor.validations.user_logout_validator import UserLogoutInputDtoValidator


class UserLogoutUseCase:
    """ This class is responsible for user logout.
    """

    def __init__(
            self,
            presenter: UserLogoutPresenterInterface,
            # repository: UserRepositoryInterface,
            config: Type[Config],
            logger: LoggerInterface,
            session_manager: SessionManagerInterface
    ):
        self.presenter = presenter
        # self.repository = repository
        self.config = config
        self.logger = logger
        self.session_manager = session_manager

    def execute(
            self,
            input_dto: UserLogoutInputDto
    ) -> Dict:

        validator = UserLogoutInputDtoValidator(input_dto.to_dict())
        validator.validate()

        try:
            self.config.DEALER_CLIENT.PFCLogout()
        except LogoutFailedException as e:
            self.logger.log_exception(f"Account {input_dto.account} logout exception raised at {datetime.now()}: {e}")
            raise LogoutFailedException("Logout failed")

        self.session_manager.destroy_session()

        output_dto = UserLogoutOutputDto(account=input_dto.account, is_success=True)
        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info("User logout successfully")
        return presenter_response
