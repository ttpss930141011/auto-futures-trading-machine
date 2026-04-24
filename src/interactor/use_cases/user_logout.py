"""Use case for user logout."""

from typing import Dict

from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto, UserLogoutOutputDto
from src.interactor.interfaces.presenters.user_logout_presenter import UserLogoutPresenterInterface
from src.interactor.validations.user_logout_validator import UserLogoutInputDtoValidator


class UserLogoutUseCase:
    """Handles user logout operations."""

    def __init__(
        self,
        presenter: UserLogoutPresenterInterface,
        service_container: ServiceContainer,
    ) -> None:
        self.presenter = presenter
        self.service_container = service_container

    def execute(self, input_dto: UserLogoutInputDto) -> Dict:
        UserLogoutInputDtoValidator(input_dto.to_dict()).validate()

        self.service_container.exchange_api.client.PFCLogout()
        self.service_container.session_repository.destroy_session()

        output_dto = UserLogoutOutputDto(account=input_dto.account, is_success=True)
        presenter_response = self.presenter.present(output_dto)
        self.service_container.logger.log_info("User logout successfully")
        return presenter_response
