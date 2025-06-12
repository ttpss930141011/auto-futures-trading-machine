from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.send_market_order_presenter import SendMarketOrderPresenter
from src.app.cli_pfcf.views.send_market_order_view import SendMarketOrderView
from src.domain.value_objects import OrderOperation, OpenClose, DayTrade, TimeInForce, OrderTypeEnum
from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto
from src.interactor.errors.error_classes import NotFountItemException
from src.interactor.use_cases.send_market_order import SendMarketOrderUseCase


class SendMarketOrderController(CliMemoryControllerInterface):
    """ User register item
    """

    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository
        self.condition_repository = service_container.condition_repository

    def _get_user_input(self) -> SendMarketOrderInputDto:

        order_account = self.session_repository.get_order_account()
        item_code = self.session_repository.get_item_code()

        if order_account is None:
            raise NotFountItemException("Please select order account first")

        if item_code is None:
            raise NotFountItemException("Please select item first")

        side_input = input("Enter side (b/s): ")
        side = OrderOperation.BUY if side_input == "b" else OrderOperation.SELL
        quantity = int(input("Enter quantity: "))

        input_dto = SendMarketOrderInputDto(
            order_account=order_account,
            item_code=item_code,
            side=side,
            order_type=OrderTypeEnum.Market,
            price=0,  # market order does not need price
            quantity=quantity,
            open_close=OpenClose.AUTO,
            note="",
            day_trade=DayTrade.No,
            time_in_force=TimeInForce.IOC
        )

        return input_dto

    def execute(self):
        """ Execute the creating condition controller
        """
        if self.session_repository.is_user_logged_in() is False:
            self.logger.log_info("User not login")
            return
        presenter = SendMarketOrderPresenter()
        input_dto = self._get_user_input()
        use_case = SendMarketOrderUseCase(presenter, self.service_container, self.logger, self.session_repository)
        result = use_case.execute(input_dto)
        view = SendMarketOrderView()
        view.show(result)
