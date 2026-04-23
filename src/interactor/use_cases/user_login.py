"""Use case for user login."""

from datetime import datetime
from typing import Dict

from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.user_login_dtos import UserLoginInputDto, UserLoginOutputDto
from src.interactor.errors.error_classes import LoginFailedException, ItemNotCreatedException
from src.interactor.interfaces.presenters.user_login_presenter import UserLoginPresenterInterface
from src.interactor.interfaces.repositories.user_repository import UserRepositoryInterface
from src.interactor.validations.user_login_validator import UserLoginInputDtoValidator


class UserLoginUseCase:
    """Handles user login operations."""

    def __init__(
        self,
        presenter: UserLoginPresenterInterface,
        repository: UserRepositoryInterface,
        service_container: ServiceContainer,
    ) -> None:
        self.presenter = presenter
        self.repository = repository
        self.service_container = service_container

    def execute(self, input_dto: UserLoginInputDto) -> Dict:
        UserLoginInputDtoValidator(input_dto.to_dict()).validate()

        logger = self.service_container.logger
        exchange_client = self.service_container.exchange_api.client

        try:
            exchange_client.PFCLogin(
                input_dto.account, input_dto.password, input_dto.ip_address
            )
        except LoginFailedException as e:
            logger.log_exception(
                f"Account {input_dto.account} login exception raised at {datetime.now()}: {e}"
            )
            raise LoginFailedException("Login failed")

        user = self.repository.get(input_dto.account)
        if not user:
            user = self.repository.create(
                account=input_dto.account,
                password=input_dto.password,
                ip_address=input_dto.ip_address,
                client=exchange_client,
            )
            if not user:
                logger.log_error(f"User {input_dto.account} not created")
                raise ItemNotCreatedException(input_dto.account, "User")

        self.service_container.session_repository.create_session(account=user.account)

        presenter_response = self.presenter.present(UserLoginOutputDto(user))
        logger.log_info("User login successfully")
        return presenter_response
