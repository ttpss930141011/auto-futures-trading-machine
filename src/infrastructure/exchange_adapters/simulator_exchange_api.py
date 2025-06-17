"""Simulator Exchange API - Mock implementation for testing."""

from typing import Any, Callable, Dict, List, Optional
import logging
import uuid
from datetime import datetime

from src.domain.interfaces.exchange_api_interface import (
    ExchangeApiInterface,
    LoginCredentials,
    LoginResult,
    OrderRequest,
    OrderResult,
    Position
)


class SimulatorExchangeApi(ExchangeApiInterface):
    """Simulator implementation for testing without real exchange connection."""
    
    def __init__(self):
        """Initialize simulator."""
        self._logger = logging.getLogger(__name__)
        self._connected = False
        self._positions: Dict[str, Position] = {}
        self._orders: Dict[str, OrderRequest] = {}
        self._balances: Dict[str, float] = {
            "cash": 1000000.0,
            "margin": 500000.0
        }
        self._market_data_callbacks: List[Callable] = []
        
    def connect(self, credentials: LoginCredentials) -> LoginResult:
        """Simulate connection."""
        self._logger.info(f"Simulator connecting with user: {credentials.username}")
        
        # Simulate login validation
        if credentials.username == "test" and credentials.password == "test":
            self._connected = True
            return LoginResult(
                success=True,
                message="Successfully connected to simulator",
                session_id=f"SIM_{uuid.uuid4().hex[:8]}"
            )
        else:
            return LoginResult(
                success=False,
                message="Invalid credentials for simulator",
                error_code="SIM_AUTH_FAILED"
            )
    
    def disconnect(self) -> bool:
        """Simulate disconnection."""
        self._connected = False
        self._logger.info("Simulator disconnected")
        return True
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected
    
    def send_order(self, order: OrderRequest) -> OrderResult:
        """Simulate order sending."""
        if not self._connected:
            return OrderResult(
                success=False,
                message="Not connected to simulator",
                error_code="SIM_NOT_CONNECTED"
            )
        
        # Generate order ID
        order_id = f"SIM_{uuid.uuid4().hex[:8]}"
        
        # Store order
        self._orders[order_id] = order
        
        # Simulate order execution
        self._logger.info(f"Simulator executing order: {order_id} - {order.symbol} {order.side} {order.quantity}")
        
        # Update positions
        self._update_positions(order)
        
        return OrderResult(
            success=True,
            order_id=order_id,
            message="Order executed successfully in simulator",
            timestamp=datetime.now().isoformat()
        )
    
    def cancel_order(self, order_id: str, account: str) -> bool:
        """Simulate order cancellation."""
        if order_id in self._orders:
            del self._orders[order_id]
            self._logger.info(f"Simulator cancelled order: {order_id}")
            return True
        return False
    
    def get_positions(self, account: str) -> List[Position]:
        """Get simulated positions."""
        return list(self._positions.values())
    
    def get_account_balance(self, account: str) -> Dict[str, float]:
        """Get simulated account balance."""
        return self._balances.copy()
    
    def subscribe_market_data(self, symbols: List[str], callback: Callable) -> bool:
        """Simulate market data subscription."""
        self._market_data_callbacks.append(callback)
        self._logger.info(f"Simulator subscribed to symbols: {symbols}")
        
        # Could start a thread here to generate fake ticks
        return True
    
    def unsubscribe_market_data(self, symbols: List[str]) -> bool:
        """Simulate market data unsubscription."""
        self._logger.info(f"Simulator unsubscribed from symbols: {symbols}")
        return True
    
    def get_exchange_name(self) -> str:
        """Get exchange name."""
        return "Simulator (Test Exchange)"
    
    # Private helper methods
    
    def _update_positions(self, order: OrderRequest) -> None:
        """Update positions based on order."""
        key = f"{order.account}_{order.symbol}"
        
        if key in self._positions:
            pos = self._positions[key]
            if order.side == 'BUY':
                pos.quantity += order.quantity
            else:
                pos.quantity -= order.quantity
                
            # Remove position if quantity is 0
            if pos.quantity == 0:
                del self._positions[key]
        else:
            # Create new position
            self._positions[key] = Position(
                account=order.account,
                symbol=order.symbol,
                quantity=order.quantity if order.side == 'BUY' else -order.quantity,
                side='LONG' if order.side == 'BUY' else 'SHORT',
                average_price=order.price,
                unrealized_pnl=0.0,
                realized_pnl=0.0
            )