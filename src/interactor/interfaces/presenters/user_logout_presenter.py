from abc import ABC, abstractmethod
from typing import Dict

from src.interactor.dtos.user_logout_dtos import UserLogoutOutputDto


class UserLogoutPresenterInterface(ABC):

    @abstractmethod
    def present(self, output_dto: UserLogoutOutputDto) -> Dict:
        """ Present the UserLogout
        """
