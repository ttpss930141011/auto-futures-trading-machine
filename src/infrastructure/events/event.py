"""Event system base classes for futures trading machine.

This module defines the core abstractions for the event-driven architecture:
- Event: Base class for all events
- Producer: Active component that generates events
- EventSource: Interface for event sources
- FifoQueueEventSource: FIFO queue implementation of EventSource
"""
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Optional, List, TypeVar, Generic

# Type variable for Event subclasses
E = TypeVar('E')


class Event:
    """Base class for events in the system.
    
    An event is something that occurs at a specific point in time.
    
    Args:
        when: The datetime when the event occurred.
    """
    def __init__(self, when: datetime):
        self.when: datetime = when


class Producer:
    """Base class for producers.
    
    A producer is the active part that generates events.
    """
    async def initialize(self):
        """Initialize the producer."""
        pass

    async def main(self):
        """Run the loop that produces events."""
        pass

    async def finalize(self):
        """Perform cleanup."""
        pass


class EventSource(metaclass=ABCMeta):
    """Base class for event sources.
    
    This class declares the interface for retrieving events.
    
    Args:
        producer: Optional producer associated with this event source.
    """
    def __init__(self, producer: Optional[Producer] = None):
        self.producer = producer

    @abstractmethod
    def pop(self) -> Optional[Event]:
        """Return the next event, or None if no events are available.
        
        Returns:
            The next event or None
        """
        raise NotImplementedError()


class FifoQueueEventSource(EventSource, Generic[E]):
    """A FIFO queue event source.
    
    This class provides event buffering capabilities.
    
    Args:
        producer: Optional producer associated with this event source
        events: Optional list of initial events
        max_size: Maximum size of the queue (0 for unlimited)
    """
    def __init__(
        self, 
        producer: Optional[Producer] = None, 
        events: Optional[List[E]] = None,
        max_size: int = 0
    ):
        super().__init__(producer)
        self._queue: List[E] = []
        self._max_size = max_size
        if events:
            self._queue.extend(events)

    def push(self, event: E) -> bool:
        """Add an event to the end of the queue.
        
        Args:
            event: The event to add
            
        Returns:
            True if the event was added, False if the queue is full
        """
        if self._max_size > 0 and len(self._queue) >= self._max_size:
            return False
        self._queue.append(event)
        return True

    def pop(self) -> Optional[E]:
        """Remove and return the next event in the queue.
        
        Returns:
            The oldest event in the queue, or None if the queue is empty
        """
        if not self._queue:
            return None
        return self._queue.pop(0)
    
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
    
    def clear(self) -> None:
        """Remove all events from the queue."""
        self._queue.clear()
    
    def peek(self) -> Optional[E]:
        """Look at the next event without removing it.
        
        Returns:
            The oldest event in the queue, or None if the queue is empty
        """
        if not self._queue:
            return None
        return self._queue[0]