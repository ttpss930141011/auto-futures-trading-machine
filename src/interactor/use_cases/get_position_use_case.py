"""
GetPositionUseCase: orchestrates retrieving and presenting position data.
"""

from typing import Dict

from src.interactor.dtos.get_position_dtos import GetPositionInputDto, GetPositionOutputDto
from src.interactor.interfaces.repositories.position_repository_interface import (
    PositionRepositoryInterface,
)
from src.interactor.interfaces.presenters.position_presenter_interface import (
    PositionPresenterInterface,
)
from src.interactor.interfaces.logger.logger import LoggerInterface


class GetPositionUseCase:
    """Use case for fetching real-time positions."""

    def __init__(
        self,
        repository: PositionRepositoryInterface,
        presenter: PositionPresenterInterface,
        logger: LoggerInterface,
    ):
        """
        Args:
            repository: Provides position data.
            presenter: Formats output.
            logger: Records events and errors.
        """
        self._repository = repository
        self._presenter = presenter
        self._logger = logger

    def execute(self, input_dto: GetPositionInputDto) -> Dict:
        """
        Fetch positions and return the presented output.

        Args:
            input_dto: DTO containing customer and product identifiers.

        Returns:
            A primitive structure as defined by the presenter.
        """
        try:
            self._logger.log_info(
                f"Querying positions for account={input_dto.order_account}, product={input_dto.product_id}"
            )
            positions = self._repository.get_positions(
                input_dto.order_account, input_dto.product_id
            )
            output_dto = GetPositionOutputDto(positions=positions)
        except Exception as e:
            self._logger.log_error(f"Position query failed: {e}")
            output_dto = GetPositionOutputDto(positions=[], error=str(e))

        return self._presenter.present(output_dto)
