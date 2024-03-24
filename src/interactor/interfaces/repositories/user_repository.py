""" This module contains the interface for the UserRepository
"""

from abc import ABC, abstractmethod
from typing import Optional, Any

from src.domain.entities.user import User


class UserRepositoryInterface(ABC):
    """ This class is the interface for the UserRepository
    """

    @abstractmethod
    def get(self, account: str) -> Optional[User]:
        """ Get a User by account

        :param account: account
        :return: User
        """

    @abstractmethod
    def create(self, account: str, password: str, ip_address: str, client: Any) -> Optional[User]:
        """ Create a new User

        :param account: account
        :param password: password
        :param ip_address: ip_address
        :param client: Any
        :return: User
        """
