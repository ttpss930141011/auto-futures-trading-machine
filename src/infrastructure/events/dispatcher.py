"""Event dispatcher for futures trading machine.

This module provides a realtime event dispatcher that supports both event source
and event type based subscription models, with enhanced support for event buffering.
"""
import asyncio
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any, Set, Tuple

from src.infrastructure.events.event import Event, EventSource, FifoQueueEventSource


EventHandler = Callable[[Event], Any]
IdleHandler = Callable[[], Any]
SchedulerJob = Callable[[], Any]


class ScheduledJob:
    """A job scheduled to run at a specific time."""
    
    def __init__(self, when: datetime, job: SchedulerJob):
        """Initialize a scheduled job.
        
        Args:
            when: The time when the job should run
            job: The function to execute
        """
        self.when = when
        self.job = job

    def __lt__(self, other):
        """Compare jobs by scheduled time."""
        return self.when < other.when


class SchedulerQueue:
    """Queue for scheduling jobs to run at specific times."""
    
    def __init__(self):
        """Initialize an empty scheduler queue."""
        self._queue: List[ScheduledJob] = []

    def push(self, when: datetime, job: SchedulerJob):
        """Add a job to the queue.
        
        Args:
            when: The time when the job should run
            job: The function to execute
        """
        import heapq
        heapq.heappush(self._queue, ScheduledJob(when, job))

    def pop(self) -> Optional[SchedulerJob]:
        """Get the next job that's ready to run.
        
        Returns:
            The next job function if one is ready, otherwise None
        """
        import heapq
        if self._queue and self._queue[0].when <= datetime.utcnow():
            return heapq.heappop(self._queue).job
        return None

    def peek(self) -> Optional[datetime]:
        """Get the time of the next scheduled job.
        
        Returns:
            The datetime of the next job, or None if queue is empty
        """
        if self._queue:
            return self._queue[0].when
        return None


class EventMultiplexer:
    """Multiplex events from multiple sources.
    
    This class manages multiple event sources and provides a unified
    interface to retrieve events from all sources in the correct order.
    """
    
    def __init__(self):
        """Initialize an empty event multiplexer."""
        self._sources: Set[EventSource] = set()
        self._prefetched_events: Dict[EventSource, Optional[Event]] = {}

    def add_source(self, source: EventSource) -> None:
        """Add an event source to the multiplexer.
        
        Args:
            source: The event source to add
        """
        if source not in self._sources:
            self._sources.add(source)
            self._prefetched_events[source] = None

    def peek_next_event_time(self) -> Optional[datetime]:
        """Get the time of the next available event across all sources.
        
        Returns:
            The datetime of the next event, or None if no events are available
        """
        self._prefetch_events()
        
        # Find the event with the earliest timestamp
        next_events = [event for event in self._prefetched_events.values() if event]
        if not next_events:
            return None
        
        return min(event.when for event in next_events)

    def pop_next_event(self) -> Tuple[Optional[EventSource], Optional[Event]]:
        """Get the oldest event from any source.
        
        Returns:
            A tuple of (source, event), or (None, None) if no events are available
        """
        self._prefetch_events()
        
        next_source = None
        next_event = None
        
        # Find the event with the earliest timestamp
        for source, event in self._prefetched_events.items():
            if event and (next_event is None or event.when < next_event.when):
                next_source = source
                next_event = event
        
        # Consume the event if found
        if next_source:
            self._prefetched_events[next_source] = None
            
        return (next_source, next_event)
    
    def _prefetch_events(self) -> None:
        """Prefetch the next event from each source for sorting."""
        for source in self._sources:
            if self._prefetched_events[source] is None:
                self._prefetched_events[source] = source.pop()


class RealtimeDispatcher:
    """Event dispatcher that supports both event source and event type subscriptions.
    
    This dispatcher integrates event buffering capabilities with FifoQueueEventSource
    while maintaining compatibility with direct event handling.
    """
    
    def __init__(self, logger=None):
        """Initialize the dispatcher.
        
        Args:
            logger: Optional logger for error messages
        """
        # Store event handlers by event type (string)
        self._event_handlers: Dict[str, List[EventHandler]] = {}
        
        # Store event handlers by event source
        self._source_handlers: Dict[EventSource, List[EventHandler]] = {}
        
        # Event source multiplexer
        self._event_mux = EventMultiplexer()
        
        # Event buffers for high-frequency events
        self._event_buffers: Dict[str, FifoQueueEventSource] = {}
        
        # Scheduler for timed jobs
        self._scheduler_queue = SchedulerQueue()
        
        # Handlers to call when there are no events to process
        self._idle_handlers: List[IdleHandler] = []
        
        # Running state
        self._running = False
        
        # Logger
        self._logger = logger or logging.getLogger(__name__)

    def subscribe_event_type(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to events of a specific type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: Function to call when an event of this type is published
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        if handler not in self._event_handlers[event_type]:
            self._event_handlers[event_type].append(handler)

    def publish_event(self, event_type: str, event: Event) -> None:
        """Publish an event to all subscribers of the specified type.
        
        If there are no immediate subscribers, the event is buffered
        for later processing using a FifoQueueEventSource.
        
        Args:
            event_type: The type of event being published
            event: The event object
        """
        # Create buffer if one doesn't exist for this event type
        if event_type not in self._event_buffers:
            self._event_buffers[event_type] = FifoQueueEventSource()
            # Add to multiplexer if we're using source-based dispatch
            self._event_mux.add_source(self._event_buffers[event_type])
        
        # Add to buffer for deferred processing
        self._event_buffers[event_type].push(event)
        
        # Also dispatch immediately if there are subscribers
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self._log_error(f"Error handling event: {e}")

    def subscribe(self, source: EventSource, event_handler: EventHandler) -> None:
        """Subscribe to events from a specific source.
        
        Args:
            source: The event source to subscribe to
            event_handler: Function to call when the source produces an event
        """
        assert not self._running, "Subscribing once we're running is not currently supported."
        
        # Register source with multiplexer
        self._event_mux.add_source(source)
        
        # Store handler
        handlers = self._source_handlers.setdefault(source, [])
        if event_handler not in handlers:
            handlers.append(event_handler)

    def buffer_events(self, event_type: str, max_events: int = 100) -> FifoQueueEventSource:
        """Get or create an event buffer for a specific event type.
        
        This can be used to manually buffer events for batch processing.
        
        Args:
            event_type: The type of event to buffer
            max_events: Maximum number of events to buffer (not yet implemented)
            
        Returns:
            A FifoQueueEventSource that buffers events of the specified type
        """
        if event_type not in self._event_buffers:
            self._event_buffers[event_type] = FifoQueueEventSource()
            self._event_mux.add_source(self._event_buffers[event_type])
        
        return self._event_buffers[event_type]

    def schedule(self, when: datetime, job: SchedulerJob) -> None:
        """Schedule a job to run at a specific time.
        
        Args:
            when: The time when the job should run
            job: The function to execute
        """
        self._scheduler_queue.push(when, job)

    def subscribe_idle(self, handler: IdleHandler) -> None:
        """Register a handler to be called when there are no events to process.
        
        Args:
            handler: Function to call during idle time
        """
        if handler not in self._idle_handlers:
            self._idle_handlers.append(handler)

    async def run(self) -> None:
        """Run the event dispatcher loop."""
        self._running = True
        try:
            while self._running:
                # Process scheduled jobs
                self._process_scheduled_jobs()
                
                # Process events from sources
                self._process_source_events()
                
                # Call idle handlers if no events are pending
                if not self._scheduler_queue.peek():
                    await self._on_idle()

                # Small delay to prevent CPU hogging
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            self._log_info("Event dispatcher cancelled")
            raise
        except Exception as e:
            self._log_error(f"Error in event dispatcher: {e}")
            raise
        finally:
            self._running = False

    async def stop(self) -> None:
        """Stop the event dispatcher."""
        self._running = False

    def _process_scheduled_jobs(self) -> None:
        """Process all scheduled jobs that are due."""
        while job := self._scheduler_queue.pop():
            try:
                job()
            except Exception as e:
                self._log_error(f"Error executing scheduled job: {e}")

    def _process_source_events(self) -> None:
        """Process events from all sources."""
        source, event = self._event_mux.pop_next_event()
        if source and event:
            # Dispatch to handlers for this source
            if source in self._source_handlers:
                for handler in self._source_handlers[source]:
                    try:
                        handler(event)
                    except Exception as e:
                        self._log_error(f"Error handling event from source: {e}")

    async def _on_idle(self) -> None:
        """Call idle handlers when there are no events to process."""
        if self._idle_handlers:
            for handler in self._idle_handlers:
                try:
                    await handler()
                except Exception as e:
                    self._log_error(f"Error in idle handler: {e}")
        else:
            # Prevent CPU hogging when there are no idle handlers
            await asyncio.sleep(0.1)
    
    def _log_error(self, message: str) -> None:
        """Log an error message."""
        if self._logger:
            self._logger.error(message)
        else:
            print(f"ERROR: {message}")
            
    def _log_info(self, message: str) -> None:
        """Log an info message."""
        if self._logger:
            self._logger.info(message)
        else:
            print(f"INFO: {message}")