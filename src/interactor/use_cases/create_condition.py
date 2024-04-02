""" This module is responsible for creating a new profession.
"""
from typing import Dict

from src.app.cli_pfcf.config import Config
from src.interactor.dtos.create_condition_dtos import CreateConditionInputDto, CreateConditionOutputDto
from src.interactor.errors.error_classes import LoginFailedException, ItemNotCreatedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.create_condition_presenter import CreateConditionPresenterInterface
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.create_condition_validator import CreateConditionInputDtoValidator


class CreateConditionUseCase:
    """ This class is responsible for creating a new profession.
        """

    def __init__(
            self,
            presenter: CreateConditionPresenterInterface,
            condition_repository: ConditionRepositoryInterface,
            config: Config,
            logger: LoggerInterface,
            session_repository: SessionRepositoryInterface,
    ):
        self.presenter = presenter
        self.condition_repository = condition_repository
        self.config = config
        self.logger = logger
        self.session_repository = session_repository

    def execute(
            self,
            input_dto: CreateConditionInputDto
    ) -> Dict:
        """ This method is responsible for creating a new condition.
        :param input_dto: The input data transfer object.
        :type input_dto: CreateConditionInputDto
        :return: Dict
        """

        validator = CreateConditionInputDtoValidator(input_dto.to_dict())
        validator.validate()

        user = self.session_repository.get_current_user()

        if user is None:
            error = LoginFailedException("User not logged in")
            self.logger.log_info(str(error))
            raise error

        condition = self.condition_repository.create(
            action=input_dto.action,
            trigger_price=input_dto.trigger_price,
            turning_point=input_dto.turning_point,
            quantity=input_dto.quantity,
            take_profit_point=input_dto.take_profit_point,
            stop_loss_point=input_dto.stop_loss_point,
            is_following=False
        )

        all_conditions = self.condition_repository.get_all()
        print(f'all data {all_conditions}')

        if condition is None:
            error = ItemNotCreatedException(input_dto.to_dict(), "Condition")
            self.logger.log_exception(str(error))
            raise error

        output_dto = CreateConditionOutputDto(condition)
        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info("Condition created successfully")
        return presenter_response
