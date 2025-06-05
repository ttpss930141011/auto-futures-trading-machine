"""
Position repository interface.
"""

from abc import ABC, abstractmethod
from typing import List

from src.interactor.dtos.get_position_dtos import PositionDto


class PositionRepositoryInterface(ABC):
    """Abstraction for retrieving position data."""

    @abstractmethod
    def get_positions(self, order_account: str, product_id: str) -> List[PositionDto]:
        """Fetch positions for the given account and product."""
        ...
