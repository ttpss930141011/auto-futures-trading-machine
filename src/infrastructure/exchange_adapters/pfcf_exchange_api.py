"""PFCF Exchange API Implementation - Concrete implementation for Taiwan Unified Futures."""

from typing import Any, Callable, Dict, List, Optional
import logging

from src.domain.interfaces.exchange_api_interface import (
    ExchangeApiInterface,
    LoginCredentials,
    LoginResult,
    OrderRequest,
    OrderResult,
    Position
)
from src.infrastructure.pfcf_client.api import PFCFApi
from src.infrastructure.exchange_adapters.pfcf_converter import PFCFConverter
from src.infrastructure.exchange_adapters.pfcf_event_adapter import PFCFEventAdapter
from src.infrastructure.events.exchange_event_manager import ExchangeEventManager
from src.infrastructure.services.service_container import ServiceContainer
from src.domain.interfaces.exchange_event_interface import ExchangeEventManagerInterface


class PFCFExchangeApi(ExchangeApiInterface):
    """PFCF (Taiwan Unified Futures) implementation of ExchangeApiInterface."""
    
    def __init__(self, service_container: ServiceContainer):
        """Initialize PFCF Exchange API.
        
        Args:
            service_container: Service container with dependencies
        """
        self._logger = logging.getLogger(__name__)
        self._service_container = service_container
        self._pfcf_api = service_container.exchange_api  # This is the existing PFCFApi
        self._converter = PFCFConverter()
        self._connected = False
        
        # Create event management system
        self._event_manager = ExchangeEventManager("PFCF")
        self._event_adapter = PFCFEventAdapter(self._pfcf_api.client, self._event_manager)
        
    def connect(self, credentials: LoginCredentials) -> LoginResult:
        """Connect to PFCF exchange."""
        try:
            # Use existing PFCFApi login method
            login_params = {
                "user_id": credentials.username,
                "password": credentials.password,
                "is_test_env": credentials.environment == 'test'
            }
            
            success = self._pfcf_api.PFCLogin(**login_params)
            
            if success:
                self._connected = True
                # Connect all events after successful login
                self._event_adapter.connect_all_events()
                return LoginResult(
                    success=True,
                    message="Successfully connected to PFCF",
                    session_id=self._pfcf_api.user_id
                )
            else:
                return LoginResult(
                    success=False,
                    message="Failed to connect to PFCF",
                    error_code="LOGIN_FAILED"
                )
                
        except Exception as e:
            self._logger.error(f"PFCF connection error: {e}")
            return LoginResult(
                success=False,
                message=str(e),
                error_code="CONNECTION_ERROR"
            )
    
    def disconnect(self) -> bool:
        """Disconnect from PFCF exchange."""
        try:
            # Disconnect all events before disconnecting
            self._event_adapter.disconnect_all_events()
            # PFCF doesn't have explicit disconnect, just mark as disconnected
            self._connected = False
            return True
        except Exception as e:
            self._logger.error(f"PFCF disconnect error: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to PFCF."""
        return self._connected and self._pfcf_api.user_id is not None
    
    def send_order(self, order: OrderRequest) -> OrderResult:
        """Send order to PFCF exchange."""
        try:
            # Convert to PFCF format
            pfcf_order = self._convert_to_pfcf_order(order)
            
            # Send order using PFCF API
            result = self._pfcf_api.trade.Order(pfcf_order)
            
            # Convert result back
            return self._convert_pfcf_result(result)
            
        except Exception as e:
            self._logger.error(f"PFCF order error: {e}")
            return OrderResult(
                success=False,
                message=str(e),
                error_code="ORDER_ERROR"
            )
    
    def cancel_order(self, order_id: str, account: str) -> bool:
        """Cancel order on PFCF exchange."""
        try:
            # PFCF cancel order implementation
            # Note: This needs to be implemented based on PFCF API
            self._logger.warning("Cancel order not yet implemented for PFCF")
            return False
        except Exception as e:
            self._logger.error(f"PFCF cancel order error: {e}")
            return False
    
    def get_positions(self, account: str) -> List[Position]:
        """Get positions from PFCF exchange."""
        try:
            # Use existing position repository
            pfcf_positions = self._service_container.position_repository.get_by_user_id(
                self._pfcf_api.user_id
            )
            
            # Convert to standard Position format
            return [self._convert_pfcf_position(pos) for pos in pfcf_positions]
            
        except Exception as e:
            self._logger.error(f"PFCF get positions error: {e}")
            return []
    
    def get_account_balance(self, account: str) -> Dict[str, float]:
        """Get account balance from PFCF exchange."""
        try:
            # This needs to be implemented based on PFCF API
            self._logger.warning("Get account balance not yet implemented for PFCF")
            return {}
        except Exception as e:
            self._logger.error(f"PFCF get balance error: {e}")
            return {}
    
    def subscribe_market_data(self, symbols: List[str], callback: Callable) -> bool:
        """Subscribe to PFCF market data."""
        try:
            # This is handled by MarketDataGatewayService
            # Just return True for now as it's managed elsewhere
            return True
        except Exception as e:
            self._logger.error(f"PFCF subscribe error: {e}")
            return False
    
    def unsubscribe_market_data(self, symbols: List[str]) -> bool:
        """Unsubscribe from PFCF market data."""
        try:
            # This is handled by MarketDataGatewayService
            # Just return True for now as it's managed elsewhere
            return True
        except Exception as e:
            self._logger.error(f"PFCF unsubscribe error: {e}")
            return False
    
    def get_exchange_name(self) -> str:
        """Get exchange name."""
        return "PFCF (Taiwan Unified Futures)"
    
    def get_event_manager(self) -> ExchangeEventManagerInterface:
        """Get the event manager for this exchange."""
        return self._event_manager
    
    # Private helper methods
    
    def _convert_to_pfcf_order(self, order: OrderRequest) -> Dict[str, Any]:
        """Convert standard OrderRequest to PFCF format."""
        from src.domain.enums import OrderOperation, OrderTypeEnum, TimeInForce
        
        # Map standard fields to internal enums
        side_enum = OrderOperation.BUY if order.side == 'BUY' else OrderOperation.SELL
        order_type_enum = OrderTypeEnum.Market if order.order_type == 'MARKET' else OrderTypeEnum.Limit
        tif_enum = TimeInForce.IOC  # Default to IOC
        
        return {
            "ACTNO": order.account,
            "PRODUCTID": order.symbol,
            "BS": self._converter.convert_side(side_enum),
            "ODTYPE": self._converter.convert_order_type(order_type_enum),
            "PRICE": self._converter.format_price(order.price, order.symbol),
            "ORDERQTY": str(order.quantity),
            "TIMEINFORCE": self._converter.convert_time_in_force(tif_enum),
            "OPENCLOSE": "0",  # AUTO
            "DAYTRADE": "0",   # No day trade
            "NOTE": order.note or "From AFTM"
        }
    
    def _convert_pfcf_result(self, pfcf_result: Any) -> OrderResult:
        """Convert PFCF result to standard OrderResult."""
        if pfcf_result and hasattr(pfcf_result, 'Success'):
            return OrderResult(
                success=pfcf_result.Success,
                order_id=getattr(pfcf_result, 'OrderID', None),
                message=getattr(pfcf_result, 'Message', None),
                error_code=getattr(pfcf_result, 'ErrorCode', None)
            )
        else:
            return OrderResult(
                success=False,
                message="Invalid PFCF result"
            )
    
    def _convert_pfcf_position(self, pfcf_pos: Any) -> Position:
        """Convert PFCF position to standard Position."""
        # This is a simplified conversion - adjust based on actual PFCF position structure
        return Position(
            account=pfcf_pos.account_id,
            symbol=pfcf_pos.symbol,
            quantity=abs(pfcf_pos.quantity),
            side='LONG' if pfcf_pos.quantity > 0 else 'SHORT',
            average_price=pfcf_pos.average_price,
            unrealized_pnl=0.0,  # Need to calculate
            realized_pnl=0.0     # Need to calculate
        )