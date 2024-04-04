""" Module for the UserLoginPresenterInterface
"""

from abc import ABC, abstractmethod
from typing import Dict

from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountOutputDto


class SelectOrderAccountPresenterInterface(ABC):
    """ Class for the Interface of the CreateMarketOrderPresenter
    """

    @abstractmethod
    def present(self, output_dto: SelectOrderAccountOutputDto) -> Dict:
        """ Present the output dto
        """
