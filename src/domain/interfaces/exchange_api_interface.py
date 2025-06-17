"""Exchange API Interface - Abstract interface for broker APIs."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class LoginCredentials:
    """Standard login credentials."""
    
    username: str
    password: str
    server_url: str
    environment: str  # 'test' or 'prod'


@dataclass
class LoginResult:
    """Standard login result."""
    
    success: bool
    message: str
    session_id: Optional[str] = None
    error_code: Optional[str] = None


@dataclass
class OrderRequest:
    """Broker-neutral order request."""
    
    account: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    order_type: str  # 'MARKET', 'LIMIT', etc.
    quantity: int
    price: float
    time_in_force: str  # 'IOC', 'FOK', 'GTC'
    note: Optional[str] = None


@dataclass
class OrderResult:
    """Broker-neutral order result."""
    
    success: bool
    order_id: Optional[str] = None
    message: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class Position:
    """Broker-neutral position."""
    
    account: str
    symbol: str
    quantity: int
    side: str  # 'LONG' or 'SHORT'
    average_price: float
    unrealized_pnl: float
    realized_pnl: float


class ExchangeApiInterface(ABC):
    """Abstract interface for exchange/broker APIs."""
    
    @abstractmethod
    def connect(self, credentials: LoginCredentials) -> LoginResult:
        """Connect to the exchange/broker."""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the exchange/broker."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the exchange/broker."""
        pass
    
    @abstractmethod
    def send_order(self, order: OrderRequest) -> OrderResult:
        """Send an order to the exchange."""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, account: str) -> bool:
        """Cancel an existing order."""
        pass
    
    @abstractmethod
    def get_positions(self, account: str) -> List[Position]:
        """Get current positions for an account."""
        pass
    
    @abstractmethod
    def get_account_balance(self, account: str) -> Dict[str, float]:
        """Get account balance information."""
        pass
    
    @abstractmethod
    def subscribe_market_data(self, symbols: List[str], callback: Callable) -> bool:
        """Subscribe to market data for given symbols."""
        pass
    
    @abstractmethod
    def unsubscribe_market_data(self, symbols: List[str]) -> bool:
        """Unsubscribe from market data."""
        pass
    
    @abstractmethod
    def get_exchange_name(self) -> str:
        """Get the name of the exchange/broker."""
        pass