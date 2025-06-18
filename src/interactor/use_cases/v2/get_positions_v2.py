"""Get Positions V2 Use Case - Using abstracted exchange interface."""

import logging
from typing import List

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
            raw_positions = self._exchange_api.get_positions(input_dto.account_id)
            
            # Convert raw data to PositionDto
            position_dtos = []
            for raw_pos in raw_positions:
                # Create PositionDto from raw data
                # Adapt based on the actual structure of raw position data
                position_dto = self._create_position_dto(raw_pos)
                position_dtos.append(position_dto)
            
            self._logger.info(
                f"Retrieved {len(position_dtos)} positions from "
                f"{self._exchange_api.get_exchange_name()}"
            )
            
            return GetPositionOutputDto(
                success=True,
                positions=position_dtos,
                message=f"Retrieved {len(position_dtos)} positions"
            )
            
        except Exception as e:
            self._logger.error(f"Error getting positions: {e}")
            return GetPositionOutputDto(
                success=False,
                positions=[],
                message=str(e)
            )
    
    def _create_position_dto(self, raw_position: dict) -> PositionDto:
        """Create PositionDto from raw exchange data.
        
        Args:
            raw_position: Raw position data from exchange
            
        Returns:
            PositionDto instance
        """
        # This is a simplified mapping - adjust based on actual exchange data
        return PositionDto(
            account_id=raw_position.get('account_id', ''),
            symbol=raw_position.get('symbol', ''),
            net_qty=raw_position.get('quantity', 0),
            
            # Map additional fields as needed
            today_buy_qty=raw_position.get('today_buy_qty', 0),
            today_sell_qty=raw_position.get('today_sell_qty', 0),
            yd_qty=raw_position.get('yd_qty', 0),
            
            avg_price=raw_position.get('average_price', 0.0),
            last_price=raw_position.get('last_price', 0.0),
            settle_price=raw_position.get('settle_price', 0.0),
            
            unrealized_pnl=raw_position.get('unrealized_pnl', 0.0),
            realized_pnl=raw_position.get('realized_pnl', 0.0),
            
            open_interest=raw_position.get('open_interest', 0),
            margin_requirement=raw_position.get('margin_requirement', 0.0),
            
            market_value=raw_position.get('market_value', 0.0),
            account_balance=raw_position.get('account_balance', 0.0),
            free_cash=raw_position.get('free_cash', 0.0),
            order_margin=raw_position.get('order_margin', 0.0),
            position_margin=raw_position.get('position_margin', 0.0),
            
            buy_trades=raw_position.get('buy_trades', 0),
            sell_trades=raw_position.get('sell_trades', 0)
        )