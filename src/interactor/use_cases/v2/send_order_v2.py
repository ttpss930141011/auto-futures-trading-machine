"""Send Order V2 Use Case - Using abstracted exchange interface."""

import logging

from src.domain.interfaces.exchange_api_interface import (
    ExchangeApiInterface,
    OrderRequest,
    OrderResult
)
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto, SendMarketOrderOutputDto


class SendOrderV2UseCase:
    """Send order use case using abstracted exchange interface.

    This V2 version uses the broker-agnostic ExchangeApiInterface
    instead of being tied to a specific broker implementation.
    """

    def __init__(self, exchange_api: ExchangeApiInterface):
        """Initialize with exchange API interface.

        Args:
            exchange_api: Any exchange that implements ExchangeApiInterface
        """
        self._exchange_api = exchange_api
        self._logger = logging.getLogger(__name__)

    def execute(self, input_dto: SendMarketOrderInputDto) -> SendMarketOrderOutputDto:
        """Execute order sending through abstracted interface.

        Args:
            input_dto: Order details

        Returns:
            SendMarketOrderDto with result
        """
        try:
            # Convert DTO to exchange-neutral OrderRequest
            order_request = OrderRequest(
                account=input_dto.order_account,
                symbol=input_dto.item_code,
                side=input_dto.side.value,  # Convert enum to string
                order_type=input_dto.order_type.value,
                quantity=input_dto.quantity,
                price=input_dto.price,
                time_in_force=input_dto.time_in_force.value,
                note=input_dto.note
            )

            # Send order through abstracted interface
            result: OrderResult = self._exchange_api.send_order(order_request)

            # Convert result to output DTO
            if result.success:
                self._logger.info(
                    "Order sent successfully via %s: %s",
                    self._exchange_api.get_exchange_name(),
                    result.order_id
                )
                return SendMarketOrderOutputDto(
                    is_send_order=True,
                    order_serial=result.order_id or "",
                    note=result.message or "Order sent successfully"
                )

            self._logger.error(
                "Order failed via %s: %s",
                self._exchange_api.get_exchange_name(),
                result.message
            )
            return SendMarketOrderOutputDto(
                is_send_order=False,
                order_serial="",
                note=result.message or "Order failed",
                error_code=result.error_code or "",
                error_message=result.message or "Order failed"
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            self._logger.error("Error sending order: %s", str(e))
            return SendMarketOrderOutputDto(
                is_send_order=False,
                order_serial="",
                note=str(e),
                error_message=str(e)
            )

    def get_exchange_name(self) -> str:
        """Get the name of the current exchange.

        Returns:
            Exchange/broker name
        """
        return self._exchange_api.get_exchange_name()

    def is_connected(self) -> bool:
        """Check if exchange is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._exchange_api.is_connected()
