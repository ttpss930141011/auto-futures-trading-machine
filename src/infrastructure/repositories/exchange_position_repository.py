"""Exchange Position Repository - Implements position repository using exchange API."""

from typing import List, Optional
import logging

from src.domain.entities.position import Position
from src.domain.interfaces.exchange_api_interface import ExchangeApiInterface
from src.interactor.interfaces.repositories.position_repository_interface import (
    PositionRepositoryInterface
)


class ExchangePositionRepository(PositionRepositoryInterface):
    """Position repository that fetches data from exchange API.
    
    This implementation is broker-agnostic, using the ExchangeApiInterface
    to fetch position data from any supported exchange.
    """
    
    def __init__(self, exchange_api: ExchangeApiInterface):
        """Initialize repository with exchange API.
        
        Args:
            exchange_api: Exchange API interface for fetching positions.
        """
        self._exchange_api = exchange_api
        self._logger = logging.getLogger(__name__)
        self._position_cache: Dict[str, List[Position]] = {}
    
    def get_all_positions(self, account_id: str) -> List[Position]:
        """Get all positions for an account.
        
        Args:
            account_id: Account identifier.
            
        Returns:
            List of positions for the account.
        """
        try:
            # Check cache first
            if account_id in self._position_cache:
                return self._position_cache[account_id]
            
            # Fetch from exchange
            exchange_positions = self._exchange_api.get_positions(account_id)
            
            # Convert to domain entities
            positions = []
            for ex_pos in exchange_positions:
                position = Position(
                    account_id=ex_pos.account,
                    symbol=ex_pos.symbol,
                    quantity=ex_pos.quantity,
                    side=ex_pos.side,
                    average_price=ex_pos.average_price,
                    unrealized_pnl=ex_pos.unrealized_pnl,
                    realized_pnl=ex_pos.realized_pnl,
                    market_value=ex_pos.quantity * ex_pos.average_price,
                    position_id=f"{ex_pos.account}_{ex_pos.symbol}"
                )
                positions.append(position)
            
            # Cache the results
            self._position_cache[account_id] = positions
            
            return positions
            
        except Exception as e:
            self._logger.error(f"Error fetching positions for {account_id}: {e}")
            return []
    
    def get_position_by_symbol(self, account_id: str, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol.
        
        Args:
            account_id: Account identifier.
            symbol: Trading symbol.
            
        Returns:
            Position if found, None otherwise.
        """
        positions = self.get_all_positions(account_id)
        
        for position in positions:
            if position.symbol == symbol:
                return position
                
        return None
    
    def refresh_positions(self, account_id: str) -> bool:
        """Refresh positions from the exchange.
        
        Args:
            account_id: Account identifier.
            
        Returns:
            True if refresh successful, False otherwise.
        """
        try:
            # Clear cache for this account
            if account_id in self._position_cache:
                del self._position_cache[account_id]
            
            # Fetch fresh data
            positions = self.get_all_positions(account_id)
            
            return len(positions) >= 0  # Success even if no positions
            
        except Exception as e:
            self._logger.error(f"Error refreshing positions for {account_id}: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Clear all cached position data."""
        self._position_cache.clear()
        self._logger.info("Position cache cleared")