"""This module is responsible for registering items in the trading system.

This use case handles the registration of trading items by validating user sessions,
checking item availability, and registering the item with the exchange client.
"""
from typing import Dict

from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.register_item_dtos import RegisterItemInputDto, RegisterItemOutputDto
from src.interactor.errors.error_classes import LoginFailedException, NotFountItemException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.register_item_presenter import RegisterItemPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.register_item_validator import RegisterItemInputDtoValidator


class RegisterItemUseCase:
    """Use case for registering trading items.

    This class handles the business logic for registering trading items,
    including validation, session management, and exchange client interactions.
    """

    def __init__(
            self,
            presenter: RegisterItemPresenterInterface,
            service_container: ServiceContainer,
    ) -> None:
        """Initialize the RegisterItemUseCase.

        Args:
            presenter: The presenter interface for formatting output.
            service_container: Container providing access to all required services.
        """
        self.presenter = presenter
        self.service_container = service_container

    def execute(
            self,
            input_dto: RegisterItemInputDto
    ) -> Dict:
        """Execute the register item use case.

        Args:
            input_dto: The input data transfer object containing registration details.

        Returns:
            Dict: The formatted response from the presenter.

        Raises:
            LoginFailedException: If the user is not logged in.
            NotFountItemException: If the requested item is not found.
        """

        validator = RegisterItemInputDtoValidator(input_dto.to_dict())
        validator.validate()

        user = self.service_container.session_repository.get_current_user()

        if user is None:
            raise LoginFailedException(f"Account {input_dto.account} not login")

        items_object_list = self.service_container.exchange_client.PFCGetFutureData("")
        items_list = [items_object_list[i].COMMODITYID for i in range(len(items_object_list))]

        if input_dto.item_code not in items_list:
            raise NotFountItemException(f"{input_dto.item_code} is not found")

        self.service_container.exchange_client.DQuoteLib.RegItem(input_dto.item_code)  # Register item
        self.service_container.session_repository.set_item_code(input_dto.item_code)

        output_dto = RegisterItemOutputDto(account=input_dto.account, item_code=input_dto.item_code, is_registered=True)
        presenter_response = self.presenter.present(output_dto)
        self.service_container.logger.log_info(f"Account {input_dto.account} register item {input_dto.item_code} successfully")
        return presenter_response
