"""PFCF Exchange API Implementation - Concrete implementation for Taiwan Unified Futures."""

from typing import Any, Callable, Dict, List
import logging

from src.domain.interfaces.exchange_api_interface import (
    ExchangeApiInterface,
    LoginCredentials,
    LoginResult,
    OrderRequest,
    OrderResult
)
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

            return LoginResult(
                success=False,
                message="Failed to connect to PFCF",
                error_code="LOGIN_FAILED"
            )

        except Exception as e:
            self._logger.error("PFCF connection error: %s", e)
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
            self._logger.error("PFCF disconnect error: %s", e)
            return False
    def is_connected(self) -> bool:
        """Check if connected to PFCF."""
        return self._connected and self._pfcf_api.user_id is not None
    def send_order(self, order: OrderRequest) -> OrderResult:
        """Send order to PFCF exchange."""
        try:
            # Create PFCF OrderObject
            pfcf_order = self._pfcf_api.trade.OrderObject()

            # Use EnumConverter to get PFCF enum values
            from src.infrastructure.services.enum_converter import EnumConverter  # pylint: disable=import-outside-toplevel
            enum_converter = EnumConverter(self._pfcf_api)

            # Map internal enums from OrderRequest
            from src.domain.value_objects import (  # pylint: disable=import-outside-toplevel
                OrderOperation, OrderTypeEnum, TimeInForce, OpenClose, DayTrade
            )

            # Convert string values to internal enums
            side_enum = OrderOperation.BUY if order.side == 'BUY' else OrderOperation.SELL
            order_type_enum = OrderTypeEnum.Market if order.order_type == 'MARKET' else OrderTypeEnum.Limit
            tif_map = {
                'IOC': TimeInForce.IOC,
                'FOK': TimeInForce.FOK,
                'GTC': TimeInForce.ROD  # Map GTC to ROD for PFCF
            }
            tif_enum = tif_map.get(order.time_in_force, TimeInForce.IOC)

            # Set fields on OrderObject using PFCF enums
            pfcf_order.ACTNO = order.account
            pfcf_order.PRODUCTID = order.symbol
            pfcf_order.BS = enum_converter.to_pfcf_enum(side_enum)
            pfcf_order.ORDERTYPE = enum_converter.to_pfcf_enum(order_type_enum)
            pfcf_order.PRICE = enum_converter.to_pfcf_decimal(order.price)
            pfcf_order.ORDERQTY = order.quantity
            pfcf_order.TIMEINFORCE = enum_converter.to_pfcf_enum(tif_enum)
            pfcf_order.OPENCLOSE = enum_converter.to_pfcf_enum(OpenClose.AUTO)
            pfcf_order.DTRADE = enum_converter.to_pfcf_enum(DayTrade.No)
            pfcf_order.NOTE = order.note or "From AFTM"

            # Send order using PFCF API
            result = self._pfcf_api.client.DTradeLib.Order(pfcf_order)

            # Convert result back
            return self._convert_pfcf_result(result)

        except Exception as e:
            self._logger.error("PFCF order error: %s", e)
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
            self._logger.error("PFCF cancel order error: %s", e)
            return False
    def get_positions(self, account: str) -> List[Dict[str, Any]]:
        """Get positions from PFCF exchange."""
        try:
            # Use existing position repository
            pfcf_positions = self._service_container.position_repository.get_by_user_id(
                self._pfcf_api.user_id
            )

            # Convert PFCF positions to dictionaries
            positions = []
            for pos in pfcf_positions:
                # pos is PositionDto from PFCF
                position_dict = pos.to_dict() if hasattr(pos, 'to_dict') else vars(pos)
                positions.append(position_dict)
            return positions

        except Exception as e:
            self._logger.error("PFCF get positions error: %s", e)
            return []
    def get_account_balance(self, account: str) -> Dict[str, float]:
        """Get account balance from PFCF exchange."""
        try:
            # This needs to be implemented based on PFCF API
            self._logger.warning("Get account balance not yet implemented for PFCF")
            return {}
        except Exception as e:
            self._logger.error("PFCF get balance error: %s", e)
            return {}
    def subscribe_market_data(self, symbols: List[str], callback: Callable) -> bool:
        """Subscribe to PFCF market data."""
        try:
            # This is handled by MarketDataGatewayService
            # Just return True for now as it's managed elsewhere
            return True
        except Exception as e:
            self._logger.error("PFCF subscribe error: %s", e)
            return False
    def unsubscribe_market_data(self, symbols: List[str]) -> bool:
        """Unsubscribe from PFCF market data."""
        try:
            # This is handled by MarketDataGatewayService
            # Just return True for now as it's managed elsewhere
            return True
        except Exception as e:
            self._logger.error("PFCF unsubscribe error: %s", e)
            return False
    def get_exchange_name(self) -> str:
        """Get exchange name."""
        return "PFCF (Taiwan Unified Futures)"
    def get_event_manager(self) -> ExchangeEventManagerInterface:
        """Get the event manager for this exchange."""
        return self._event_manager

    # Private helper methods
    def _convert_pfcf_result(self, pfcf_result: Any) -> OrderResult:
        """Convert PFCF result to standard OrderResult."""
        if pfcf_result:
            # Check for ISSEND attribute (based on SendMarketOrderUseCase)
            is_success = getattr(pfcf_result, 'ISSEND', False)
            error_code = getattr(pfcf_result, 'ERRORCODE', '')
            error_msg = getattr(pfcf_result, 'ERRORMSG', '')
            order_seq = getattr(pfcf_result, 'SEQ', '')

            return OrderResult(
                success=is_success and not error_msg,
                order_id=order_seq,
                message=error_msg or "Order sent successfully",
                error_code=error_code if error_code else None
            )

        return OrderResult(
            success=False,
            message="Invalid PFCF result"
        )
