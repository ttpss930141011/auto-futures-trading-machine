""" Module for the UserLoginPresenterInterface
"""

from abc import ABC, abstractmethod
from typing import Dict

from src.interactor.dtos.send_market_order_dtos import SendMarketOrderOutputDto


class SendMarketOrderPresenterInterface(ABC):
    """ Class for the Interface of the CreateMarketOrderPresenter
    """

    @abstractmethod
    def present(self, output_dto: SendMarketOrderOutputDto) -> Dict:
        """ Present the output dto
        """
