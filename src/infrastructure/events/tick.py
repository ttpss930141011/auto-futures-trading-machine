from datetime import datetime
from src.infrastructure.events.event import Event

class Tick:
    """Simplified tick data structure with essential trading information."""
    
    def __init__(self, commodity_id: str, match_price: float):
        """Initialize a tick with minimal required data.
        
        Args:
            commodity_id: The code of the futures contract
            match_price: Current match price
        """
        self.commodity_id = commodity_id
        self.match_price = match_price


class TickEvent(Event):
    """An event containing tick data."""
    
    def __init__(self, when: datetime, tick: Tick):
        """Initialize a tick event.
        
        Args:
            when: The datetime when the event occurred
            tick: The tick data
        """
        super().__init__(when)
        self.tick = tick