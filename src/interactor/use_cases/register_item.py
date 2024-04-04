""" This module is responsible for creating a new profession.
"""
from typing import Dict

from src.app.cli_pfcf.config import Config
from src.interactor.dtos.register_item_dtos import RegisterItemInputDto, RegisterItemOutputDto
from src.interactor.errors.error_classes import LoginFailedException, NotFountItemException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.register_item_presenter import RegisterItemPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.register_item_validator import RegisterItemInputDtoValidator


class RegisterItemUseCase:
    """ This class is responsible for creating a new profession.
    """

    def __init__(
            self,
            presenter: RegisterItemPresenterInterface,
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
            input_dto: RegisterItemInputDto
    ) -> Dict:
        """ This method is responsible for registering a new item.
        :param input_dto: The input data transfer object.
        :type input_dto: RegisterItemInputDto
        :return: Dict
        """

        validator = RegisterItemInputDtoValidator(input_dto.to_dict())
        validator.validate()

        user = self.session_repository.get_current_user()

        if user is None:
            raise LoginFailedException(f"Account {input_dto.account} not login")

        items_object_list = self.config.EXCHANGE_CLIENT.PFCGetFutureData("")
        items_list = [items_object_list[i].COMMODITYID for i in range(len(items_object_list))]

        if input_dto.item_code not in items_list:
            raise NotFountItemException(f"{input_dto.item_code} is not found")

        self.config.EXCHANGE_CLIENT.DQuoteLib.RegItem(input_dto.item_code)  # Register item
        self.session_repository.set_item_code(input_dto.item_code)

        output_dto = RegisterItemOutputDto(account=input_dto.account, item_code=input_dto.item_code, is_registered=True)
        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info(f"Account {input_dto.account} register item {input_dto.item_code} successfully")
        return presenter_response
