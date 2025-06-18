"""PFCF Event Adapter - Converts PFCF events to standard events."""

import logging
from datetime import datetime
from typing import Any, Callable, Dict

from src.domain.interfaces.exchange_event_interface import (
    Event,
    EventType,
    TickEvent,
    OrderEvent,
    PositionEvent
)
from src.infrastructure.events.exchange_event_manager import ExchangeEventManager


class PFCFEventAdapter:
    """Adapts PFCF COM events to standard event system."""
    
    def __init__(self, pfcf_client: Any, event_manager: ExchangeEventManager):
        """Initialize PFCF event adapter.
        
        Args:
            pfcf_client: PFCF client with COM event properties
            event_manager: Standard event manager to emit events to
        """
        self._client = pfcf_client
        self._event_manager = event_manager
        self._logger = logging.getLogger(__name__)
        self._registered_handlers: Dict[str, Callable] = {}
        
    def connect_all_events(self) -> None:
        """Connect all PFCF events to the standard event system."""
        # Connection events
        self._connect_event(
            "PFCloginStatus",
            self._create_login_handler()
        )
        self._connect_event(
            "PFCErrorData",
            self._create_error_handler()
        )
        
        # Quote events
        self._connect_quote_event(
            "OnConnected",
            self._create_connected_handler()
        )
        self._connect_quote_event(
            "OnDisconnected",
            self._create_disconnected_handler()
        )
        self._connect_quote_event(
            "OnTickDataTrade",
            self._create_tick_handler()
        )
        
        # Trade events
        self._connect_trade_event(
            "OnReply",
            self._create_order_reply_handler()
        )
        self._connect_trade_event(
            "OnMatch",
            self._create_order_match_handler()
        )
        
        # Account events
        self._connect_account_event(
            "OnPositionData",
            self._create_position_handler()
        )
        
    def disconnect_all_events(self) -> None:
        """Disconnect all PFCF events."""
        # Disconnect all registered handlers
        for event_path, handler in self._registered_handlers.items():
            try:
                parts = event_path.split('.')
                if len(parts) == 1:
                    # Direct client event
                    setattr(self._client, event_path, 
                           getattr(self._client, event_path).__isub__(handler))
                else:
                    # Library event
                    lib = getattr(self._client, parts[0])
                    setattr(lib, parts[1], 
                           getattr(lib, parts[1]).__isub__(handler))
                           
                self._logger.debug(f"Disconnected handler from {event_path}")
            except Exception as e:
                self._logger.error(f"Error disconnecting {event_path}: {e}")
                
        self._registered_handlers.clear()
    
    def _connect_event(self, event_name: str, handler: Callable) -> None:
        """Connect a direct client event."""
        try:
            # Use += operator
            setattr(self._client, event_name,
                   getattr(self._client, event_name).__iadd__(handler))
            self._registered_handlers[event_name] = handler
            self._logger.debug(f"Connected handler to {event_name}")
        except Exception as e:
            self._logger.error(f"Error connecting {event_name}: {e}")
    
    def _connect_quote_event(self, event_name: str, handler: Callable) -> None:
        """Connect a DQuoteLib event."""
        self._connect_library_event("DQuoteLib", event_name, handler)
    
    def _connect_trade_event(self, event_name: str, handler: Callable) -> None:
        """Connect a DTradeLib event."""
        self._connect_library_event("DTradeLib", event_name, handler)
    
    def _connect_account_event(self, event_name: str, handler: Callable) -> None:
        """Connect a DAccountLib event."""
        self._connect_library_event("DAccountLib", event_name, handler)
    
    def _connect_library_event(self, library: str, event_name: str, handler: Callable) -> None:
        """Connect a library-specific event."""
        try:
            lib = getattr(self._client, library)
            # Use += operator
            setattr(lib, event_name,
                   getattr(lib, event_name).__iadd__(handler))
            event_path = f"{library}.{event_name}"
            self._registered_handlers[event_path] = handler
            self._logger.debug(f"Connected handler to {event_path}")
        except Exception as e:
            self._logger.error(f"Error connecting {library}.{event_name}: {e}")
    
    # Handler creators
    
    def _create_login_handler(self) -> Callable:
        """Create handler for login status."""
        def handler(user_id: str, status_code: str):
            event_type = EventType.LOGIN_SUCCESS if status_code == "0" else EventType.LOGIN_FAILED
            event = Event(
                event_type=event_type,
                timestamp=datetime.now().isoformat(),
                data={
                    "user_id": user_id,
                    "status_code": status_code
                },
                source="PFCF",
                error=None if status_code == "0" else f"Login failed: {status_code}"
            )
            self._event_manager.emit(event)
        return handler
    
    def _create_error_handler(self) -> Callable:
        """Create handler for errors."""
        def handler(error_code: str, error_msg: str):
            event = Event(
                event_type=EventType.ERROR,
                timestamp=datetime.now().isoformat(),
                data={
                    "error_code": error_code,
                    "error_message": error_msg
                },
                source="PFCF",
                error=f"{error_code}: {error_msg}"
            )
            self._event_manager.emit(event)
        return handler
    
    def _create_connected_handler(self) -> Callable:
        """Create handler for connection."""
        def handler():
            event = Event(
                event_type=EventType.CONNECTED,
                timestamp=datetime.now().isoformat(),
                data={},
                source="PFCF"
            )
            self._event_manager.emit(event)
        return handler
    
    def _create_disconnected_handler(self) -> Callable:
        """Create handler for disconnection."""
        def handler():
            event = Event(
                event_type=EventType.DISCONNECTED,
                timestamp=datetime.now().isoformat(),
                data={},
                source="PFCF"
            )
            self._event_manager.emit(event)
        return handler
    
    def _create_tick_handler(self) -> Callable:
        """Create handler for tick data."""
        def handler(commodity_id: str, trade_time: str, trade_price: str,
                   trade_quantity: str, total_volume: str, tick_type: str,
                   bid_price: str, bid_quantity: str, ask_price: str, ask_quantity: str):
            try:
                tick = TickEvent(
                    event_type=EventType.TICK_DATA,
                    timestamp=trade_time,
                    data={
                        "tick_type": tick_type,
                        "total_volume": int(total_volume)
                    },
                    source="PFCF",
                    symbol=commodity_id,
                    price=float(trade_price),
                    volume=int(trade_quantity),
                    bid=float(bid_price),
                    ask=float(ask_price),
                    bid_volume=int(bid_quantity),
                    ask_volume=int(ask_quantity)
                )
                self._event_manager.emit(tick)
            except Exception as e:
                self._logger.error(f"Error processing tick data: {e}")
        return handler
    
    def _create_order_reply_handler(self) -> Callable:
        """Create handler for order replies."""
        def handler(order_data: Any):
            try:
                # Map PFCF status to standard status
                status_map = {
                    "0": "accepted",
                    "1": "rejected",
                    # Add more mappings as needed
                }
                status = status_map.get(str(order_data.STATUS), "unknown")
                
                order_event = OrderEvent(
                    event_type=EventType.ORDER_ACCEPTED,  # Will be set in __post_init__
                    timestamp=datetime.now().isoformat(),
                    data={
                        "raw_status": order_data.STATUS,
                        "message": getattr(order_data, "MESSAGE", "")
                    },
                    source="PFCF",
                    order_id=str(order_data.SEQ),
                    account=order_data.ACTNO,
                    symbol=order_data.PRODUCTID,
                    side="BUY" if order_data.BS == "0" else "SELL",
                    quantity=int(order_data.ORDERQTY),
                    price=float(order_data.PRICE),
                    status=status
                )
                self._event_manager.emit(order_event)
            except Exception as e:
                self._logger.error(f"Error processing order reply: {e}")
        return handler
    
    def _create_order_match_handler(self) -> Callable:
        """Create handler for order matches (fills)."""
        def handler(match_data: Any):
            try:
                order_event = OrderEvent(
                    event_type=EventType.ORDER_FILLED,
                    timestamp=datetime.now().isoformat(),
                    data={
                        "fill_price": float(match_data.MATCHPRICE),
                        "fill_quantity": int(match_data.MATCHQTY),
                        "fill_time": match_data.MATCHTIME
                    },
                    source="PFCF",
                    order_id=str(match_data.SEQ),
                    account=match_data.ACTNO,
                    symbol=match_data.PRODUCTID,
                    side="BUY" if match_data.BS == "0" else "SELL",
                    quantity=int(match_data.MATCHQTY),
                    price=float(match_data.MATCHPRICE),
                    status="filled"
                )
                self._event_manager.emit(order_event)
            except Exception as e:
                self._logger.error(f"Error processing order match: {e}")
        return handler
    
    def _create_position_handler(self) -> Callable:
        """Create handler for position data."""
        def handler(position_data: Any):
            try:
                position = PositionEvent(
                    event_type=EventType.POSITION_UPDATE,
                    timestamp=datetime.now().isoformat(),
                    data={
                        "raw_data": str(position_data)
                    },
                    source="PFCF",
                    account=position_data.ACTNO,
                    symbol=position_data.PRODUCTID,
                    quantity=abs(int(position_data.NETQTY)),
                    side="LONG" if int(position_data.NETQTY) > 0 else "SHORT",
                    average_price=float(position_data.AVGPRICE),
                    unrealized_pnl=float(getattr(position_data, "UNREALPNL", 0)),
                    realized_pnl=float(getattr(position_data, "REALPNL", 0))
                )
                self._event_manager.emit(position)
            except Exception as e:
                self._logger.error(f"Error processing position data: {e}")
        return handler