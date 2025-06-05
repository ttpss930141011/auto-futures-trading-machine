"""
Presenter for the GetPosition use case.
"""

from typing import Dict

from src.interactor.dtos.get_position_dtos import GetPositionOutputDto
from src.interactor.interfaces.presenters.position_presenter_interface import PositionPresenterInterface


class GetPositionPresenter(PositionPresenterInterface):
    """Formats GetPositionOutputDto for CLI display."""

    def present(self, output_dto: GetPositionOutputDto) -> Dict:
        """
        Convert the output DTO into a primitive dict.

        Args:
            output_dto: The output DTO containing positions and error.

        Returns:
            A dict with action, error, and positions list.
        """
        result: Dict = {
            "action": "get_positions",
            "error": output_dto.error,
            "positions": [p.__dict__ for p in output_dto.positions],
        }
        return result
