"""Market Data Gateway Service V2 - Uses new event system."""

from typing import Optional, TYPE_CHECKING

from src.domain.interfaces.exchange_api_interface import ExchangeApiInterface
from src.domain.interfaces.exchange_event_interface import (
    Event,
    EventType,
    TickEvent,
    ExchangeEventHandlerInterface
)
from src.infrastructure.messaging.zmq_tick_publisher import ZmqTickPublisher
from src.infrastructure.events.tick_event import TickEvent as LegacyTickEvent
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.app.cli_pfcf.config import Config

if TYPE_CHECKING:
    import zmq


class MarketDataGatewayServiceV2(ExchangeEventHandlerInterface):
    """Market Data Gateway Service using the new event system.
    
    This service subscribes to exchange events and publishes them via ZMQ.
    It decouples the exchange-specific event system from the ZMQ messaging.
    """

    def __init__(
        self,
        config: Config,
        logger: LoggerInterface,
        exchange_api: ExchangeApiInterface,
        zmq_context: Optional["zmq.Context"] = None,
    ):
        """Initialize market data gateway service.

        Args:
            config: Configuration object
            logger: Logger interface for logging
            exchange_api: Exchange API implementing the new interface
            zmq_context: Optional ZMQ context
        """
        self.config = config
        self.logger = logger
        self.exchange_api = exchange_api
        self._tick_publisher: Optional[ZmqTickPublisher] = None
        self._zmq_context = zmq_context
        self._subscribed = False

    def initialize_market_data_publisher(self) -> bool:
        """Initialize the market data publisher components.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create ZMQ publisher for broadcasting ticks
            bind_address = f"tcp://*:{self.config.ZMQ_TICK_PORT}"
            self._tick_publisher = ZmqTickPublisher(
                bind_address=bind_address,
                context=self._zmq_context,
                logger=self.logger,
            )

            self.logger.log_info(
                f"Market data publisher initialized on port {self.config.ZMQ_TICK_PORT}"
            )
            return True

        except Exception as e:
            self.logger.log_error(f"Failed to initialize market data publisher: {str(e)}")
            return False

    def connect_exchange_callbacks(self) -> bool:
        """Connect to exchange events using the new event system.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.exchange_api:
                self.logger.log_error("Exchange API not available")
                return False

            # Get event manager from exchange API
            event_manager = self.exchange_api.get_event_manager()
            
            # Subscribe to all events using handler interface
            event_manager.subscribe_all(self)
            self._subscribed = True
            
            self.logger.log_info("Connected to exchange event system")
            return True

        except Exception as e:
            self.logger.log_error(f"Failed to connect exchange callbacks: {str(e)}")
            return False
    
    def disconnect_exchange_callbacks(self) -> bool:
        """Disconnect from exchange events.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            if self._subscribed and self.exchange_api:
                event_manager = self.exchange_api.get_event_manager()
                event_manager.unsubscribe_all(self)
                self._subscribed = False
                
            self.logger.log_info("Disconnected from exchange event system")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Failed to disconnect exchange callbacks: {str(e)}")
            return False

    # ExchangeEventHandlerInterface implementation
    
    def on_event(self, event: Event) -> None:
        """Handle any event (generic handler)."""
        # Log all events for debugging
        self.logger.log_debug(f"Received event: {event.event_type.value}")
    
    def on_tick(self, tick: TickEvent) -> None:
        """Handle tick data by publishing to ZMQ."""
        try:
            # Convert new TickEvent to legacy format for compatibility
            legacy_tick = LegacyTickEvent(
                symbol=tick.symbol,
                price=tick.price,
                volume=tick.volume,
                timestamp=tick.timestamp,
                bid_price=tick.bid,
                ask_price=tick.ask,
                bid_volume=tick.bid_volume,
                ask_volume=tick.ask_volume,
                tick_type=tick.data.get("tick_type", "0"),
                total_volume=tick.data.get("total_volume", 0)
            )
            
            # Publish via ZMQ
            if self._tick_publisher:
                self._tick_publisher.publish_tick_event(legacy_tick)
                self.logger.log_debug(f"Published tick for {tick.symbol} at {tick.price}")
            
        except Exception as e:
            self.logger.log_error(f"Error publishing tick: {e}")
    
    def on_order(self, order: 'OrderEvent') -> None:
        """Handle order updates."""
        # Currently not used in market data gateway
        pass
    
    def on_position(self, position: 'PositionEvent') -> None:
        """Handle position updates."""
        # Currently not used in market data gateway
        pass
    
    def on_error(self, error: Event) -> None:
        """Handle errors."""
        self.logger.log_error(f"Exchange error: {error.error}")

    def cleanup_zmq(self) -> None:
        """Close market data ZMQ sockets and terminate context gracefully."""
        self.logger.log_info("Cleaning up market data ZMQ resources...")

        # Disconnect from exchange events first
        self.disconnect_exchange_callbacks()

        # Close ZMQ publisher
        if self._tick_publisher:
            try:
                self._tick_publisher.close()
                self.logger.log_info("Tick Publisher closed successfully.")
            except Exception as e:
                self.logger.log_error(f"Error closing Tick Publisher: {str(e)}")

        # Terminate the context if we own it
        if self._zmq_context and not hasattr(self._zmq_context, "_external"):
            try:
                self._zmq_context.term()
                self.logger.log_info("ZMQ context terminated successfully.")
            except Exception as e:
                self.logger.log_error(f"Error terminating ZMQ context: {str(e)}")

        self.logger.log_info("Market data ZMQ cleanup completed.")