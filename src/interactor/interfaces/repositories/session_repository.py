from abc import ABC, abstractmethod
from typing import Any


class SessionRepositoryInterface(ABC):
    @abstractmethod
    def create_session(self, account: str) -> None:
        pass

    @abstractmethod
    def get_current_user(self) -> Any:
        pass

    @abstractmethod
    def is_user_logged_in(self) -> bool:
        pass

    @abstractmethod
    def destroy_session(self) -> None:
        pass

    @abstractmethod
    def renew_session(self) -> None:
        pass

    @abstractmethod
    def get_order_account(self) -> str:
        pass

    @abstractmethod
    def set_order_account(self, account: str) -> None:
        pass

    @abstractmethod
    def set_order_account_set(self, account_set: str) -> None:
        pass

    @abstractmethod
    def set_item_code(self, item_code: str) -> None:
        pass

    @abstractmethod
    def get_item_code(self) -> str:
        pass
