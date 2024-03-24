""" This module is responsible for creating a new profession.
"""
from datetime import datetime
from typing import Dict

from config import Config
from src.interactor.dtos.user_login_dtos import UserLoginInputDto, UserLoginOutputDto
from src.interactor.errors.error_classes import LoginFailedException, ItemNotCreatedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.user_login_presenter import UserLoginPresenterInterface
from src.interactor.interfaces.repositories.user_repository import UserRepositoryInterface
from src.interactor.validations.user_login_validator import UserLoginInputDtoValidator


class UserLoginUseCase:
    """ This class is responsible for creating a new profession.
    """

    def __init__(
            self,
            presenter: UserLoginPresenterInterface,
            repository: UserRepositoryInterface,
            config: Config,
            logger: LoggerInterface
    ):
        self.presenter = presenter
        self.repository = repository
        self.config = config
        self.logger = logger

    def execute(
            self,
            input_dto: UserLoginInputDto
    ) -> Dict:
        """ This method is responsible for creating a new profession.
        :param input_dto: The input data transfer object.
        :type input_dto: UserLoginInputDto
        :return: Dict
        """

        validator = UserLoginInputDtoValidator(input_dto.to_dict())
        validator.validate()

        try:
            self.config.DEALER_CLIENT.PFCLogin(input_dto.account,
                                               input_dto.password, input_dto.ip_address)
        except LoginFailedException as e:
            self.logger.log_exception(f"Account {input_dto.account} login exception raised at {datetime.now()}: {e}")
            raise LoginFailedException("Login failed")

        user = self.repository.create(input_dto.account, input_dto.password, input_dto.ip_address,
                                      self.config.DEALER_CLIENT)
        if user is None:
            self.logger.log_exception("User creation failed")
            raise ItemNotCreatedException(input_dto.account, "User")

        output_dto = UserLoginOutputDto(user)
        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info("User login successfully")
        return presenter_response
