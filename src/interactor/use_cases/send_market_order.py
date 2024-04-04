""" This module is responsible for creating a new profession.
"""
from typing import Dict

from src.app.cli_pfcf.config import Config
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto, SendMarketOrderOutputDto
from src.interactor.errors.error_classes import LoginFailedException, ItemNotCreatedException, \
    SendMarketOrderFailedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.send_market_order_presenter import SendMarketOrderPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.send_market_order_validator import SendMarketOrderInputDtoValidator


class SendMarketOrderUseCase:
    """ This class is responsible for sending a market order.
        """

    def __init__(
            self,
            presenter: SendMarketOrderPresenterInterface,
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
            input_dto: SendMarketOrderInputDto
    ) -> Dict:
        """ This method is responsible for sending a market order.
        :param input_dto: The input data transfer object.
        :type input_dto: SendMarketOrderInputDto
        :return: Dict
        """
        validator = SendMarketOrderInputDtoValidator(input_dto.to_dict())
        validator.validate()

        user = self.session_repository.get_current_user()

        if user is None:
            raise LoginFailedException("User not logged in")

        pfcf_input = input_dto.to_pfcf_dict(self.config)
        order = self.config.EXCHANGE_TRADE.OrderObject()
        order.ACTNO = pfcf_input.get("ACTNO")
        order.PRODUCTID = pfcf_input.get("PRODUCTID")
        order.BS = pfcf_input.get("BS")
        order.ORDERTYPE = pfcf_input.get("ORDERTYPE")
        order.PRICE = pfcf_input.get("PRICE")
        order.ORDERQTY = pfcf_input.get("ORDERQTY")
        order.TIMEINFORCE = pfcf_input.get("TIMEINFORCE")
        order.OPENCLOSE = pfcf_input.get("OPENCLOSE")
        order.DTRADE = pfcf_input.get("DTRADE")
        order.NOTE = pfcf_input.get("NOTE")

        order_result = self.config.EXCHANGE_CLIENT.DTradeLib.Order(order)

        if order_result is None:
            raise ItemNotCreatedException(input_dto.order_account, "Order")
        if order_result.ERRORMSG != "":
            raise SendMarketOrderFailedException(
                f"Order not created: {order_result.ERRORMSG} with code {order_result.ERRORCODE}")

        output_dto = SendMarketOrderOutputDto(
            is_send_order=True,
            note=input_dto.note,
            order_serial=order_result.SEQ,
            error_code=order_result.ERRORCODE,
            error_message=order_result.ERRORMSG
        )

        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info("Order sent successfully")
        return presenter_response
