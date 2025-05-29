"""
Presenter interface for the GetPosition use case.
"""

from abc import ABC, abstractmethod
from typing import Dict

from src.interactor.dtos.get_position_dtos import GetPositionOutputDto


class PositionPresenterInterface(ABC):
    """Defines how to present GetPositionOutputDto."""

    @abstractmethod
    def present(self, output_dto: GetPositionOutputDto) -> Dict:
        """Convert the output DTO into a view-friendly primitive."""
        ...
