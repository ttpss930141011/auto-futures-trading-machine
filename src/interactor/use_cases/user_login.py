""" This module is responsible for creating a new profession.
"""

from datetime import datetime
from typing import Dict

from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.user_login_dtos import UserLoginInputDto, UserLoginOutputDto
from src.interactor.errors.error_classes import LoginFailedException, ItemNotCreatedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.user_login_presenter import UserLoginPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.interfaces.repositories.user_repository import UserRepositoryInterface
from src.interactor.validations.user_login_validator import UserLoginInputDtoValidator


class UserLoginUseCase:
    """Handles user login operations.

    This class follows the Single Responsibility Principle by focusing
    solely on user authentication and session management.
    """

    def __init__(
        self,
        presenter: UserLoginPresenterInterface,
        repository: UserRepositoryInterface,
        service_container: ServiceContainer,
        logger: LoggerInterface,
        session_repository: SessionRepositoryInterface,
    ) -> None:
        """Initialize the user login use case.

        Args:
            presenter: Presenter for formatting output.
            repository: Repository for user data operations.
            service_container: Container with all application services.
            logger: Logger for application logging.
            session_repository: Repository for session management.
        """
        self.presenter = presenter
        self.repository = repository
        self.service_container = service_container
        self.logger = logger
        self.session_repository = session_repository

    def execute(self, input_dto: UserLoginInputDto) -> Dict:
        """This method is responsible for creating a new user.
        :param input_dto: The input data transfer object.
        :type input_dto: UserLoginInputDto
        :return: Dict
        """

        validator = UserLoginInputDtoValidator(input_dto.to_dict())
        validator.validate()

        # Login to the dealer client
        try:
            self.service_container.exchange_client.PFCLogin(
                input_dto.account, input_dto.password, input_dto.ip_address
            )
        except LoginFailedException as e:
            self.logger.log_exception(
                f"Account {input_dto.account} login exception raised at {datetime.now()}: {e}"
            )
            raise LoginFailedException("Login failed")

        # Find the user in the repository, if not found, create a new user
        user = self.repository.get(input_dto.account)
        if not user:
            user = self.repository.create(
                account=input_dto.account,
                password=input_dto.password,
                ip_address=input_dto.ip_address,
                client=self.service_container.exchange_client,
            )
            if not user:
                self.logger.log_error(f"User {input_dto.account} not created")
                raise ItemNotCreatedException(input_dto.account, "User")

        # Create a new session in the session manager
        self.session_repository.create_session(account=user.account)

        output_dto = UserLoginOutputDto(user)
        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info("User login successfully")
        return presenter_response
