""" Module for UserInMemoryRepository
"""

from typing import Dict, Any

from src.domain.entities.user import User
from src.interactor.interfaces.repositories.user_repository import UserRepositoryInterface


class UserInMemoryRepository(UserRepositoryInterface):
    """ InMemory Repository for User
    """

    def __init__(self) -> None:
        self._data: Dict[str, User] = {}

    def get(self, account: str) -> User:
        """ Get User by account

        :param account: str
        :return: User
        """
        return self._data.get(account)

    def create(self, account: str, password: str, ip_address: str, client: Any) -> User:
        user = User(
            account=account,
            password=password,
            ip_address=ip_address,
            client=client
        )
        self._data[account] = user
        return user
