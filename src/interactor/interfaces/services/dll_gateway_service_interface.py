"""DLL Gateway Service interface for centralized exchange API access.

This interface defines the contract for accessing exchange DLL functionality
through a centralized gateway service, following the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto, SendMarketOrderOutputDto


@dataclass
class PositionInfo:
    """Data class representing position information."""
    
    account: str
    item_code: str
    quantity: int
    average_price: float
    unrealized_pnl: float


class DllGatewayServiceInterface(ABC):
    """Interface for DLL Gateway Service.
    
    Provides centralized access to exchange DLL functionality,
    ensuring single source of truth for exchange operations.
    """

    @abstractmethod
    def send_order(self, input_dto: "SendMarketOrderInputDto") -> "SendMarketOrderOutputDto":
        """Send a market order through the exchange DLL.
        
        Args:
            input_dto: SendMarketOrderInputDto containing all necessary parameters.
            
        Returns:
            SendMarketOrderOutputDto: Result of the order submission.
            
        Raises:
            DllGatewayError: If the gateway service is unavailable.
            InvalidOrderError: If the order request is invalid.
        """
        pass

    @abstractmethod
    def get_positions(self, account: str) -> List[PositionInfo]:
        """Get current positions for an account.
        
        Args:
            account: The trading account identifier.
            
        Returns:
            List of position information.
            
        Raises:
            DllGatewayError: If the gateway service is unavailable.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the DLL gateway is connected and ready.
        
        Returns:
            True if connected and ready, False otherwise.
        """
        pass

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the DLL gateway.
        
        Returns:
            Dictionary containing health status information.
        """
        pass