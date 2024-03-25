""" Module for the UserLoginPresenterInterface
"""

from abc import ABC, abstractmethod
from typing import Dict

from src.interactor.dtos.user_login_dtos import UserLoginOutputDto


class UserLoginPresenterInterface(ABC):
    """ Class for the Interface of the UserLoginPresenter
    """

    @abstractmethod
    def present(self, output_dto: UserLoginOutputDto) -> Dict:
        """ Present the output dto
        """
