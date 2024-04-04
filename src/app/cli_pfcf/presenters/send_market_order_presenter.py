""" Module for the CreateMarketOrderPresenter
"""

from typing import Dict

from src.interactor.dtos.send_market_order_dtos import SendMarketOrderOutputDto
from src.interactor.interfaces.presenters.send_market_order_presenter import SendMarketOrderPresenterInterface


class SendMarketOrderPresenter(SendMarketOrderPresenterInterface):
    """ Class for the CreateMarketOrderPresenter
    """

    def present(self, output_dto: SendMarketOrderOutputDto) -> Dict:
        """ Present the output dto
        """
        return {
            "action": "send_market_order",
            "message": f"Order with serial {output_dto.order_serial} is send: {output_dto.is_send_order}",
            "note": output_dto.note,
            "order_serial": output_dto.order_serial,
        }
