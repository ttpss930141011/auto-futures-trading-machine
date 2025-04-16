"""Event system base classes for futures trading machine.

This module defines the foundation of the event-driven architecture:
- Event: Base for all events that occur at a point in time
- Producer: Active component that generates events
- EventSource: Interface for event sources
- FifoQueueEventSource: FIFO queue implementation of EventSource for event buffering
"""
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Optional, List, TypeVar

# Type variable for Event subclasses
E = TypeVar('E', bound='Event')


class Event:
    """Base class for all events in the system.
    
    An event represents something that occurs at a specific point in time,
    such as market data updates, trading signals, or system notifications.
    
    Args:
        when: The datetime when the event occurred
    """
    def __init__(self, when: datetime):
        #: The datetime when the event occurred
        self.when: datetime = when


class Producer:
    """Base class for event producers.
    
    A producer is the active component responsible for generating events.
    It typically connects to external data sources and converts incoming
    data into system events.
    """
    async def initialize(self):
        """Initialize the producer, establishing connections and resources."""
        pass

    async def main(self):
        """Run the main loop that produces events."""
        pass

    async def finalize(self):
        """Clean up resources when the producer is no longer needed."""
        pass


class EventSource(metaclass=ABCMeta):
    """Base interface for event sources.
    
    An event source provides a common interface for the event dispatcher
    to retrieve events, regardless of where they come from.
    
    Args:
        producer: Optional producer associated with this event source
    """
    def __init__(self, producer: Optional[Producer] = None):
        self.producer = producer

    @abstractmethod
    def pop(self) -> Optional[Event]:
        """Get the next available event from this source.
        
        This method should return quickly to avoid blocking the event loop.
        
        Returns:
            The next event, or None if no events are currently available
        """
        raise NotImplementedError()


class FifoQueueEventSource(EventSource):
    """First-In-First-Out queue implementation of EventSource.
    
    This provides event buffering capabilities, allowing events to be
    collected and processed at appropriate times. It's useful for:
    1. Buffering high-frequency events
    2. Collecting events for batch processing
    3. Storing events for later replay
    4. Ensuring events are processed in the correct order
    
    Args:
        producer: Optional producer associated with this event source
        events: Optional list of initial events to populate the queue
    """
    def __init__(self, producer: Optional[Producer] = None, events: Optional[List[Event]] = None):
        super().__init__(producer)
        self._queue: List[Event] = []
        if events:
            self._queue.extend(events)

    def push(self, event: Event) -> None:
        """Add an event to the end of the queue.
        
        Args:
            event: The event to add
        """
        self._queue.append(event)

    def pop(self) -> Optional[Event]:
        """Remove and return the next event from the queue.
        
        Returns:
            The oldest event in the queue, or None if the queue is empty
        """
        if not self._queue:
            return None
        return self._queue.pop(0)
    
    def peek(self) -> Optional[Event]:
        """Look at the next event without removing it.
        
        Returns:
            The oldest event in the queue, or None if the queue is empty
        """
        if not self._queue:
            return None
        return self._queue[0]
    
    def clear(self) -> None:
        """Remove all events from the queue."""
        self._queue.clear()
    
    def size(self) -> int:
        """Get the number of events in the queue.
        
        Returns:
            The current queue size
        """
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if the queue is empty.
        
        Returns:
            True if the queue contains no events, False otherwise
        """
        return len(self._queue) == 0