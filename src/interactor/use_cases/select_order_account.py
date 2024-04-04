""" This module is responsible for creating a new profession.
"""
from typing import Dict

from src.app.cli_pfcf.config import Config
from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountInputDto, SelectOrderAccountOutputDto
from src.interactor.errors.error_classes import LoginFailedException, NotFountItemException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.select_order_account_presenter import SelectOrderAccountPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.select_order_account_validator import SelectOrderAccountInputDtoValidator


class SelectOrderAccountUseCase:
    """ This class is responsible for the use case of selecting an order account.
    """

    def __init__(
            self,
            presenter: SelectOrderAccountPresenterInterface,
            config: Config,
            logger: LoggerInterface,
            session_repository: SessionRepositoryInterface,
    ):
        self.presenter = presenter
        self.config = config
        self.logger = logger
        self.session_repository = session_repository

    def execute(
            self,
            input_dto: SelectOrderAccountInputDto
    ) -> Dict:
        """ This method is responsible for registering a new item.
        :param input_dto: The input data transfer object.
        :type input_dto: SelectOrderAccountInputDto
        :return: Dict
        """

        validator = SelectOrderAccountInputDtoValidator(input_dto.to_dict())
        validator.validate()

        user = self.session_repository.get_current_user()
        if user is None:
            raise LoginFailedException(f"User not logged in")

        order_account_set = self.config.EXCHANGE_CLIENT.UserOrderSet

        if input_dto.index >= len(order_account_set) or input_dto.order_account not in order_account_set or \
                order_account_set[input_dto.index] != input_dto.order_account:
            raise NotFountItemException(f"Order account {input_dto.order_account} not found")

        self.session_repository.set_order_account_set(order_account_set)  # Set order account set
        self.session_repository.set_order_account(input_dto.order_account)  # Set order account

        output_dto = SelectOrderAccountOutputDto(is_select_order_account=True, order_account=input_dto.order_account)
        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info(f"Order account {input_dto.order_account} selected")
        return presenter_response
