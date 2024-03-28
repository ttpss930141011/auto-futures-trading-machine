""" Module for the UserLoginPresenterInterface
"""

from abc import ABC, abstractmethod
from typing import Dict

from src.interactor.dtos.register_item_dtos import RegisterItemOutputDto


class RegisterItemPresenterInterface(ABC):
    """ Class for the Interface of the UserLoginPresenter
    """

    @abstractmethod
    def present(self, output_dto: RegisterItemOutputDto) -> Dict:
        """ Present the output dto
        """
