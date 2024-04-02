from typing import Literal

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.create_condition_presenter import CreateConditionPresenter
from src.app.cli_pfcf.views.create_condition_view import CreateConditionView
from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.create_condition_dtos import CreateConditionInputDto
from src.interactor.use_cases.create_condition import CreateConditionUseCase


class CreateConditionController(CliMemoryControllerInterface):
    """ User register item
    """

    def __init__(self, service_container: ServiceContainer):
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository
        self.condition_repository = service_container.condition_repository

    def _get_user_input(self) -> CreateConditionInputDto:
        action_input = input("Enter the action (b/s): ")
        target_price_input = input("Enter the target price: ")
        turning_point_input = input("Enter the turning point: ")
        quantity_input = input("Enter the quantity: ")
        take_profit_point_input = input("Enter the take profit point (blank for default): ")
        stop_loss_point_input = input("Enter the stop loss point (blank for default): ")

        action: Literal["buy", "sell"] = "buy" if action_input == "b" else "sell"
        target_price = int(target_price_input)
        turning_point = int(turning_point_input)
        quantity = int(quantity_input)
        take_profit_point = int(
            take_profit_point_input) if take_profit_point_input else self.config.DEFAULT_TAKE_PROFIT_POINT
        stop_loss_point = int(stop_loss_point_input) if stop_loss_point_input else self.config.DEFAULT_STOP_LOSS_POINT

        input_dto = CreateConditionInputDto(
            action=action,
            trigger_price=target_price,
            turning_point=turning_point,
            quantity=quantity,
            take_profit_point=take_profit_point,
            stop_loss_point=stop_loss_point
        )

        return input_dto

    def execute(self):
        """ Execute the creating condition controller
        """
        if self.session_repository.is_user_logged_in() is False:
            self.logger.log_info("User not login")
            return
        presenter = CreateConditionPresenter()
        input_dto = self._get_user_input()
        use_case = CreateConditionUseCase(
            presenter=presenter,
            condition_repository=self.condition_repository,
            config=self.config,
            logger=self.logger,
            session_repository=self.session_repository
        )
        result = use_case.execute(input_dto)
        view = CreateConditionView()
        view.show(result)
