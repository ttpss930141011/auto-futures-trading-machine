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
