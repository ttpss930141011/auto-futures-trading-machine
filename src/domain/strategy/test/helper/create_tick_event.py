from unittest.mock import MagicMock
import datetime
from typing import Optional

from src.infrastructure.events.tick import TickEvent, Tick


def create_tick_event(
    price: int, commodity_id: str = "TXF1", timestamp: Optional[datetime.datetime] = None
) -> TickEvent:
    """Creates a mock TickEvent."""
    if timestamp is None:
        timestamp = datetime.datetime.now(datetime.timezone.utc)

    # Mock the inner Tick object structure as needed by the strategy
    mock_tick = MagicMock(spec=Tick)
    mock_tick.match_price = price
    mock_tick.commodity_id = commodity_id

    # Create TickEvent
    tick_event = TickEvent(tick=mock_tick, when=timestamp)
    return tick_event
