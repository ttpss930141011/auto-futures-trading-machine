"""TickProducer for generating Tick events from PFCF API callbacks and publishing via ZeroMQ."""
from datetime import datetime
from typing import Optional

from src.infrastructure.messaging import ZmqPublisher, serialize
from src.infrastructure.events.tick import Tick, TickEvent
from src.interactor.interfaces.logger.logger import LoggerInterface

# Define constants for ZMQ Topics
TICK_TOPIC = b"TICK"

class TickProducer:
    """Produces tick events from raw market data and publishes them via ZeroMQ."""

    def __init__(
        self,
        tick_publisher: ZmqPublisher, # Inject ZmqPublisher
        logger: Optional[LoggerInterface] = None,
    ):
        """Initialize the tick producer with a ZMQ publisher.
        
        Args:
            # event_dispatcher: The event dispatcher
            tick_publisher: The ZeroMQ publisher for tick events.
            logger: Optional logger
            # buffer_size: Maximum number of events to buffer
        """
        self.tick_publisher = tick_publisher # Store the publisher
        self.logger = logger

        self._tick_count = 0 # Counter for occasional logging

    def handle_tick_data(
        self,
        commodity_id: str,
        info_time: str,
        match_time: str,
        match_price: str,
        match_buy_cnt: str,
        match_sell_cnt: str,
        match_quantity: str,
        match_total_qty: str,
        match_price_data,
        match_qty_data
    ) -> None:
        """Process tick data from PFCF API callback and publish via ZeroMQ.
        
        Extracts necessary data, creates a TickEvent, serializes it, 
        and publishes it using the injected ZmqPublisher.
        
        Args:
            commodity_id: The code of the futures contract
            match_price: Current match price as string
            (Other parameters are ignored)
        """
        try:             
            # Convert commodity_id to uppercase for consistency
            commodity_id = commodity_id.upper() if isinstance(commodity_id, str) else commodity_id
            
            # Convert match_price safely
            price_value = 0.0
            try:
                price_value = float(match_price)
            except (ValueError, TypeError):
                if self.logger:
                    self.logger.log_warning(f"Failed to convert price to float: {match_price}")
            
            # Create simplified tick with only needed data
            tick = Tick(
                commodity_id=commodity_id,
                match_price=price_value
            )
            
            # Create TickEvent
            tick_event = TickEvent(datetime.now(), tick)
            
            # Serialize the event using msgpack
            serialized_event = serialize(tick_event)
            
            # Publish the serialized event via ZeroMQ with TICK_TOPIC
            self.tick_publisher.publish(TICK_TOPIC, serialized_event)
    
            
            # Log occasionally based on count
            self._tick_count += 1
            if self.logger and self._tick_count % 500 == 0: # Log every 500 ticks
                self.logger.log_info(f"Published {self._tick_count} ticks via ZMQ.")
            
        except Exception as e:
            self._handle_error(e)
    
    def _handle_error(self, e):
        # Implementation of _handle_error method
        if self.logger:
            self.logger.log_error(f"Error in TickProducer handle_tick_data: {e}")
        # Depending on the error, might need more robust handling
        pass

    # Add a close method for the publisher if needed, though typically managed by the context owner
    def close(self):
        if self.logger:
              self.logger.log_info("Closing TickProducer resources (ZMQ publisher).")
        # self.tick_publisher.close() # Publisher might be shared, close at higher level
        pass