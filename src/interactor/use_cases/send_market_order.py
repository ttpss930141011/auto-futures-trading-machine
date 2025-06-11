""" This module is responsible for creating a new profession.
"""

from typing import Dict

from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.send_market_order_dtos import (
    SendMarketOrderInputDto,
    SendMarketOrderOutputDto,
)
from src.interactor.errors.error_classes import (
    LoginFailedException,
    ItemNotCreatedException,
    SendMarketOrderFailedException,
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.send_market_order_presenter import (
    SendMarketOrderPresenterInterface,
)
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.send_market_order_validator import SendMarketOrderInputDtoValidator


class SendMarketOrderUseCase:
    """Handles sending market orders to the exchange.
    
    This class follows the Single Responsibility Principle by focusing
    solely on market order execution.
    """

    def __init__(
        self,
        presenter: SendMarketOrderPresenterInterface,
        service_container: ServiceContainer,
        logger: LoggerInterface,
        session_repository: SessionRepositoryInterface,
    ) -> None:
        """Initialize the send market order use case.
        
        Args:
            presenter: Presenter for formatting output.
            service_container: Container with all application services.
            logger: Logger for application logging.
            session_repository: Repository for session management.
        """
        self.presenter = presenter
        self.service_container = service_container
        self.logger = logger
        self.session_repository = session_repository

    def execute(self, input_dto: SendMarketOrderInputDto) -> Dict:
        """This method is responsible for sending a market order.
        :param input_dto: The input data transfer object.
        :type input_dto: SendMarketOrderInputDto
        :return: Dict
        """
        validator = SendMarketOrderInputDtoValidator(input_dto.to_dict())
        validator.validate()

        user = self.session_repository.get_current_user()

        if user is None:
            raise LoginFailedException("User not logged in")

        pfcf_input = input_dto.to_pfcf_dict(self.service_container)

        print(pfcf_input)

        order = self.service_container.exchange_trade.OrderObject()
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

        order_result = self.service_container.exchange_client.DTradeLib.Order(order)

        if order_result is None:
            raise ItemNotCreatedException(input_dto.order_account, "Order")

        print("order_result.ISSEND", order_result.ISSEND)
        print("order_result.ERRORCODE", order_result.ERRORCODE)
        print("order_result.ERRORMSG", order_result.ERRORMSG)
        print("order_result.SEQ", order_result.SEQ)
        print("order_result.NOTE", order_result.NOTE)
        if order_result.ERRORMSG != "":
            raise SendMarketOrderFailedException(
                f"Order not created: {order_result.ERRORMSG} with code {order_result.ERRORCODE}"
            )

        if not order_result.ISSEND:
            raise SendMarketOrderFailedException(
                f"Order not sent (ISSEND=False), code={order_result.ERRORCODE}, msg={order_result.ERRORMSG}"
            )

        output_dto = SendMarketOrderOutputDto(
            is_send_order=order_result.ISSEND,
            note=order_result.NOTE,
            order_serial=order_result.SEQ,
            error_code=order_result.ERRORCODE,
            error_message=order_result.ERRORMSG,
        )

        presenter_response = self.presenter.present(output_dto)
        self.logger.log_info("Order sent successfully")
        return presenter_response
