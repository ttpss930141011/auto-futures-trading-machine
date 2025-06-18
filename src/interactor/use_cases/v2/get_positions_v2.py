"""Get Positions V2 Use Case - Using abstracted exchange interface."""

import logging

from src.domain.interfaces.exchange_api_interface import ExchangeApiInterface
from src.interactor.dtos.get_position_dtos import (
    GetPositionInputDto,
    GetPositionOutputDto,
    PositionDto
)


class GetPositionsV2UseCase:
    """Get positions use case using abstracted exchange interface.

    This V2 version fetches positions directly from the exchange API
    without relying on broker-specific implementations.
    """

    def __init__(self, exchange_api: ExchangeApiInterface):
        """Initialize with exchange API interface.

        Args:
            exchange_api: Any exchange that implements ExchangeApiInterface
        """
        self._exchange_api = exchange_api
        self._logger = logging.getLogger(__name__)

    def execute(self, input_dto: GetPositionInputDto) -> GetPositionOutputDto:
        """Execute position fetching through abstracted interface.

        Args:
            input_dto: Account information

        Returns:
            GetPositionOutputDto with positions
        """
        try:
            # Get raw position data from exchange
            raw_positions = self._exchange_api.get_positions(input_dto.order_account)

            # Convert raw data to PositionDto
            position_dtos = []
            for raw_pos in raw_positions:
                # Create PositionDto from raw data
                position_dto = self._create_position_dto(raw_pos)
                position_dtos.append(position_dto)

            self._logger.info(
                "Retrieved %d positions from %s",
                len(position_dtos),
                self._exchange_api.get_exchange_name()
            )

            return GetPositionOutputDto(
                positions=position_dtos
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            self._logger.error("Error getting positions: %s", str(e))
            return GetPositionOutputDto(
                positions=[],
                error=str(e)
            )

    def _create_position_dto(self, raw_position: dict) -> PositionDto:
        """Create PositionDto from raw exchange data.

        Args:
            raw_position: Raw position data from exchange

        Returns:
            PositionDto instance
        """
        # Map common fields - adapt based on actual exchange data
        return PositionDto(
            investor_account=raw_position.get('account', ''),
            product_id=raw_position.get('symbol', ''),

            # Map quantity fields
            current_long=raw_position.get('quantity', 0) if raw_position.get('side') == 'LONG' else 0,
            current_short=abs(raw_position.get('quantity', 0)) if raw_position.get('side') == 'SHORT' else 0,

            # Map price fields
            avg_cost_long=raw_position.get('average_price', 0.0) if raw_position.get('side') == 'LONG' else None,
            avg_cost_short=raw_position.get('average_price', 0.0) if raw_position.get('side') == 'SHORT' else None,

            # Map P&L fields
            unrealized_pl=raw_position.get('unrealized_pnl', 0.0),
            realized_pl=raw_position.get('realized_pnl', 0.0),

            # Optional fields with defaults
            product_kind=raw_position.get('product_kind'),
            yesterday_long=raw_position.get('yesterday_long', 0),
            yesterday_short=raw_position.get('yesterday_short', 0),
            today_order_long=raw_position.get('today_order_long', 0),
            today_order_short=raw_position.get('today_order_short', 0),
            today_filled_long=raw_position.get('today_filled_long', 0),
            today_filled_short=raw_position.get('today_filled_short', 0),
            today_closed=raw_position.get('today_closed', 0),
            reference_price=raw_position.get('reference_price'),
            currency=raw_position.get('currency', 'TWD')
        )
