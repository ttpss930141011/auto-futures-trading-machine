"""Service for initializing ZMQ Gateway components.

This service provides functionality to initialize ZeroMQ components for the gateway,
including publishers, pullers, and other messaging infrastructure.
"""

import zmq
from typing import Optional, Tuple

from src.app.cli_pfcf.config import Config
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.gateway_initializer_service_interface import (
    GatewayInitializerServiceInterface,
)
from src.infrastructure.messaging import ZmqPublisher, ZmqPuller
from src.infrastructure.pfcf_client.tick_producer import TickProducer


class GatewayInitializerService(GatewayInitializerServiceInterface):
    """Service for initializing and managing ZMQ gateway components."""

    def __init__(self, config: Config, logger: LoggerInterface) -> None:
        """Initialize the gateway initializer service.

        Args:
            config: Application configuration with ZMQ settings
            logger: Logger for recording events
        """
        self.config = config
        self.logger = logger

        # Create a shared ZMQ context
        self.zmq_context = zmq.Context.instance()

        # Store component references
        self._tick_publisher: Optional[ZmqPublisher] = None
        self._signal_puller: Optional[ZmqPuller] = None
        self._tick_producer: Optional[TickProducer] = None

        # Flag to control the initialization state
        self._is_initialized = False

    def initialize_components(self) -> bool:
        """Initialize ZMQ components for the gateway.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Log initialization attempt
            self.logger.log_info(
                f"Initializing ZMQ components with tick_pub: {self.config.ZMQ_TICK_PUB_ADDRESS}, "
                f"signal_pull: {self.config.ZMQ_SIGNAL_PULL_ADDRESS}"
            )

            # Initialize Tick Publisher
            self._tick_publisher = ZmqPublisher(
                context=self.zmq_context, address=self.config.ZMQ_TICK_PUB_ADDRESS
            )

            # Initialize Signal Puller
            self._signal_puller = ZmqPuller(
                context=self.zmq_context, address=self.config.ZMQ_SIGNAL_PULL_ADDRESS
            )

            # Initialize Tick Producer to bridge API events to ZMQ
            self._tick_producer = TickProducer(tick_publisher=self._tick_publisher)

            # Mark as initialized if everything completed successfully
            self._is_initialized = True
            self.logger.log_info("Gateway components initialized successfully")
            return True

        except Exception as e:
            self.logger.log_error(f"Failed to initialize gateway components: {str(e)}")
            self.cleanup_zmq()
            return False

    def get_components(
        self,
    ) -> Tuple[Optional[ZmqPublisher], Optional[ZmqPuller], Optional[TickProducer]]:
        """Get the initialized ZMQ components.

        Returns:
            Tuple containing the tick publisher, signal puller, and tick producer
        """
        return self._tick_publisher, self._signal_puller, self._tick_producer

    def connect_api_callbacks(self) -> bool:
        """Connect exchange API callbacks to the tick producer.

        Returns:
            bool: True if callbacks were successfully connected, False otherwise
        """
        try:
            if not self._tick_producer:
                self.logger.log_error(
                    "Cannot connect API callbacks - tick producer not initialized"
                )
                return False

            # Get the API client from config
            exchange_client = self.config.EXCHANGE_CLIENT
            if not exchange_client or not hasattr(exchange_client, "DQuoteLib"):
                self.logger.log_error("Exchange client or DQuoteLib not available")
                return False

            # Connect API callbacks to the tick producer for real-time data
            exchange_client.DQuoteLib.OnTickDataTrade += self._tick_producer.handle_tick_data
            # exchange_client.DQuoteLib.OnTickBidAsk += self._tick_producer.handle_tick_data
            # exchange_client.DQuoteLib.OnTickClose += self._tick_producer.on_tick_close
            # exchange_client.DQuoteLib.OnTickGTCStatusChange += (
            #     self._tick_producer.on_tick_gtc_status_change
            # )
            # exchange_client.DQuoteLib.OnTickHolding += self._tick_producer.on_tick_holding
            # exchange_client.DQuoteLib.OnTickNew += self._tick_producer.on_tick_new
            # exchange_client.DQuoteLib.OnTickStatics += self._tick_producer.on_tick_statics
            # exchange_client.DQuoteLib.OnTickStatus += self._tick_producer.on_tick_status
            # exchange_client.DQuoteLib.OnTickTradeInfo += self._tick_producer.on_tick_trade_info
            # exchange_client.DQuoteLib.OnTickTradeVolumeInfo += (
            #     self._tick_producer.on_tick_trade_volume_info
            # )

            self.logger.log_info("API callbacks connected to tick producer")
            return True

        except Exception as e:
            self.logger.log_error(f"Failed to connect API callbacks: {str(e)}")
            return False

    def cleanup_zmq(self) -> None:
        """Close ZMQ sockets and terminate context gracefully."""
        self.logger.log_info("Cleaning up Gateway ZMQ resources...")

        # Close sockets managed by this service
        if hasattr(self, "_tick_publisher") and self._tick_publisher:
            try:
                self._tick_publisher.close()
                self.logger.log_info("Tick Publisher closed successfully.")
            except Exception as e:
                self.logger.log_error(f"Error closing Tick Publisher: {str(e)}")

        if hasattr(self, "_signal_puller") and self._signal_puller:
            try:
                self._signal_puller.close()
                self.logger.log_info("Signal Puller closed successfully.")
            except Exception as e:
                self.logger.log_error(f"Error closing Signal Puller: {str(e)}")

        if hasattr(self, "_tick_producer") and self._tick_producer:
            try:
                self._tick_producer.close()
                self.logger.log_info("Tick Producer closed successfully.")
            except Exception as e:
                self.logger.log_error(f"Error closing Tick Producer: {str(e)}")

        # Terminate the context last
        if hasattr(self, "zmq_context") and self.zmq_context and not self.zmq_context.closed:
            try:
                self.zmq_context.term()
                self.logger.log_info("ZMQ context terminated.")
            except Exception as e:
                self.logger.log_error(f"Error terminating ZMQ context: {str(e)}")

        self._is_initialized = False

    def get_connection_addresses(self) -> Tuple[str, str]:
        """Get the ZMQ connection addresses for client applications.

        Returns:
            Tuple containing the tick subscriber address and signal push address
        """
        return self.config.ZMQ_TICK_SUB_CONNECT_ADDRESS, self.config.ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS

    @property
    def is_initialized(self) -> bool:
        """Check if the gateway components are initialized.

        Returns:
            bool: True if initialized, False otherwise
        """
        return self._is_initialized and self._tick_publisher is not None
