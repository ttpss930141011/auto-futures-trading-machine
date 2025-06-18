"""Position Repository Interface - Abstract interface for position data access."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.interactor.dtos.get_position_dtos import PositionDto


class PositionRepositoryInterface(ABC):
    """Abstract interface for position repository.
    
    This interface defines standard methods for accessing position data,
    independent of the data source (exchange API, database, etc.).
    """
    
    @abstractmethod
    def get_all_positions(self, account_id: str) -> List[PositionDto]:
        """Get all positions for an account.
        
        Args:
            account_id: Account identifier.
            
        Returns:
            List of positions for the account.
        """
        pass
    
    @abstractmethod
    def get_position_by_symbol(self, account_id: str, symbol: str) -> Optional[PositionDto]:
        """Get position for a specific symbol.
        
        Args:
            account_id: Account identifier.
            symbol: Trading symbol.
            
        Returns:
            Position if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def refresh_positions(self, account_id: str) -> bool:
        """Refresh positions from the data source.
        
        Args:
            account_id: Account identifier.
            
        Returns:
            True if refresh successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def clear_cache(self) -> None:
        """Clear any cached position data."""
        pass