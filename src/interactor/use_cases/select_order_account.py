"""This module is responsible for selecting order accounts in the trading system.

This use case handles the selection of order accounts by validating user sessions,
checking account availability, and setting the selected account in the session.
"""
from typing import Dict

from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountInputDto, SelectOrderAccountOutputDto
from src.interactor.errors.error_classes import LoginFailedException, NotFountItemException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.select_order_account_presenter import SelectOrderAccountPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.select_order_account_validator import SelectOrderAccountInputDtoValidator


class SelectOrderAccountUseCase:
    """Use case for selecting order accounts.

    This class handles the business logic for selecting order accounts,
    including validation, session management, and account verification.
    """

    def __init__(
            self,
            presenter: SelectOrderAccountPresenterInterface,
            service_container: ServiceContainer,
    ) -> None:
        """Initialize the SelectOrderAccountUseCase.

        Args:
            presenter: The presenter interface for formatting output.
            service_container: Container providing access to all required services.
        """
        self.presenter = presenter
        self.service_container = service_container

    def execute(
            self,
            input_dto: SelectOrderAccountInputDto
    ) -> Dict:
        """Execute the select order account use case.

        Args:
            input_dto: The input data transfer object containing account selection details.

        Returns:
            Dict: The formatted response from the presenter.

        Raises:
            LoginFailedException: If the user is not logged in.
            NotFountItemException: If the requested order account is not found.
        """

        validator = SelectOrderAccountInputDtoValidator(input_dto.to_dict())
        validator.validate()

        user = self.service_container.session_repository.get_current_user()
        if user is None:
            raise LoginFailedException("User not logged in")

        order_account_set = self.service_container.exchange_client.UserOrderSet

        if input_dto.index >= len(order_account_set) or input_dto.order_account not in order_account_set or \
                order_account_set[input_dto.index] != input_dto.order_account:
            raise NotFountItemException(f"Order account {input_dto.order_account} not found")

        self.service_container.session_repository.set_order_account_set(order_account_set)  # Set order account set
        self.service_container.session_repository.set_order_account(input_dto.order_account)  # Set order account

        output_dto = SelectOrderAccountOutputDto(is_select_order_account=True, order_account=input_dto.order_account)
        presenter_response = self.presenter.present(output_dto)
        self.service_container.logger.log_info(f"Order account {input_dto.order_account} selected")
        return presenter_response
