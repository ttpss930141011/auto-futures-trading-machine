""" Module for the CreateMarketOrderPresenter
"""

from typing import Dict

from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountOutputDto
from src.interactor.interfaces.presenters.select_order_account_presenter import SelectOrderAccountPresenterInterface


class SelectOrderAccountPresenter(SelectOrderAccountPresenterInterface):
    """ Class for the SelectOrderAccountPresenter"""

    def present(self, output_dto: SelectOrderAccountOutputDto) -> Dict:
        """ Present the output dto
        """
        return {
            "action": "select_order_account",
            "message": f"Order account selected: {output_dto.order_account}"
        }
