"""Use case for sending a market order."""

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
from src.interactor.interfaces.presenters.send_market_order_presenter import (
    SendMarketOrderPresenterInterface,
)
from src.interactor.validations.send_market_order_validator import SendMarketOrderInputDtoValidator


class SendMarketOrderUseCase:
    """Handles sending market orders to the exchange."""

    def __init__(
        self,
        presenter: SendMarketOrderPresenterInterface,
        service_container: ServiceContainer,
    ) -> None:
        self.presenter = presenter
        self.service_container = service_container

    def execute(self, input_dto: SendMarketOrderInputDto) -> Dict:
        SendMarketOrderInputDtoValidator(input_dto.to_dict()).validate()

        session_repository = self.service_container.session_repository
        user = session_repository.get_current_user()
        if user is None:
            raise LoginFailedException("User not logged in")

        pfcf_input = input_dto.to_pfcf_dict(self.service_container)

        print(pfcf_input)

        order = self.service_container.exchange_api.trade.OrderObject()
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

        order_result = self.service_container.exchange_api.client.DTradeLib.Order(order)

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
        self.service_container.logger.log_info("Order sent successfully")
        return presenter_response
