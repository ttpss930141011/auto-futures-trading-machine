""" This module is responsible for user logout.
"""

from typing import Dict

from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto, UserLogoutOutputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.user_logout_presenter import UserLogoutPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.user_logout_validator import UserLogoutInputDtoValidator


class UserLogoutUseCase:
    """Handles user logout operations.

    This class follows the Single Responsibility Principle by focusing
    solely on user logout and session cleanup.
    """

    def __init__(
        self,
        presenter: UserLogoutPresenterInterface,
        service_container: ServiceContainer,
        logger: LoggerInterface,
        session_manager: SessionRepositoryInterface,
    ) -> None:
        """Initialize the user logout use case.

        Args:
            presenter: Presenter for formatting output.
            service_container: Container with all application services.
            logger: Logger for application logging.
            session_manager: Repository for session management.
        """
        self.presenter = presenter
        self.service_container = service_container
        self.logger = logger
        self.session_manager = session_manager

    def execute(self, input_dto: UserLogoutInputDto) -> Dict:
        validator = UserLogoutInputDtoValidator(input_dto.to_dict())
        validator.validate()

        self.service_container.exchange_client.PFCLogout()

        self.session_manager.destroy_session()

        output_dto = UserLogoutOutputDto(account=input_dto.account, is_success=True)
        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info("User logout successfully")
        return presenter_response
