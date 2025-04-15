from typing import cast, Any, Awaitable, Callable, List, Optional
import datetime

from src.infrastructure.events.dispatcher import EventHandler, EventDispatcher
from src.infrastructure.events.event import Event, FifoQueueEventSource, Producer
from src.domain.value_objects import OrderOperation


class TradingSignal(Event):
    """A trading signal is an event that instructs to buy or sell a given pair.

    :param when: The datetime when the trading signal occurred. It must have timezone information set.
    :param operation: The operation.
    :param commodity_id: The commodity id.
    """

    def __init__(self, when: datetime.datetime, operation: OrderOperation, commodity_id: str):
        super().__init__(when)
        #: The operation.
        self.operation = operation
        #: The commodity id.
        self.commodity_id = commodity_id


class TradingSignalSource(FifoQueueEventSource):
    """Base class for event sources that generate :class:`basana.TradingSignal` events.

    :param dispatcher: The event dispatcher.
    :param producer: An optional producer associated with this event source.
    :param events: An optional list of initial events.
    """

    def __init__(
            self, dispatcher: EventDispatcher, producer: Optional[Producer] = None, events: List[Event] = []):
        super().__init__(producer=producer, events=events)
        self._dispatcher = dispatcher

    def subscribe_to_trading_signals(self, event_handler: Callable[[TradingSignal], Awaitable[Any]]):
        """Registers an async callable that will be called when a new trading signal is available.

        :param event_handler: An async callable that receives a trading signal.
        """

        self._dispatcher.subscribe(self, cast(EventHandler, event_handler))
