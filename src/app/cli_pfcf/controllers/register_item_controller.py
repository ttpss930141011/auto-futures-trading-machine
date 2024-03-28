from src.app.cli_pfcf.config import Config
from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.app.cli_pfcf.presenters.register_item_presenter import RegisterItemPresenter
from src.app.cli_pfcf.views.on_tick_data_trade_view import OnTickDataTradeView
from src.app.cli_pfcf.views.register_item_view import RegisterItemView
from src.interactor.dtos.register_item_dtos import RegisterItemInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.session_manager.session_manager import SessionManagerInterface
from src.interactor.use_cases.register_item import RegisterItemUseCase


class RegisterItemController(CliMemoryControllerInterface):
    """ User register item
    """

    def __init__(self, logger: LoggerInterface, config: Config, session_manager: SessionManagerInterface):
        self.logger = logger
        self.config = config
        self.session_manager = session_manager

    def _get_user_info(self) -> RegisterItemInputDto:
        account = self.session_manager.get_current_user()
        item_code = input("Enter item code: ")
        return RegisterItemInputDto(account, item_code)

    # @staticmethod
    # def _event_handler(*args, **kwargs):
    #     print("內期成交價報價 %s" % (", ".join(str(arg) for arg in args)))
    #     print(args, kwargs)

    @staticmethod
    def _event_handler(commodity_id, info_time, match_time, match_price, match_buy_cnt, match_sell_cnt, match_quantity,
                       match_total_qty, match_price_data, match_qty_data):
        data = {
            "commodity_id": commodity_id,
            "info_time": info_time,
            "match_time": match_time,
            "match_price": match_price,
            "match_buy_cnt": match_buy_cnt,
            "match_sell_cnt": match_sell_cnt,
            "match_quantity": match_quantity,
            "match_total_qty": match_total_qty,
            # "match_price_data": match_price_data,
            # "match_qty_data": match_qty_data
        }

        view = OnTickDataTradeView()
        view.show(data)
        return match_price_data, match_qty_data

    def execute(self):
        """ Execute the user register item
        """
        if self.session_manager.is_user_logged_in() is False:
            self.logger.log_info("User not login")
            return
        presenter = RegisterItemPresenter()
        input_dto = self._get_user_info()
        use_case = RegisterItemUseCase(presenter, self.config, self.logger, self.session_manager, self._event_handler)
        result = use_case.execute(input_dto)
        view = RegisterItemView()
        view.show(result)
