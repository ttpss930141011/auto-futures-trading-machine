"""Event dispatcher for futures trading machine.

This module provides a realtime event dispatcher that supports various
event subscription models and event handling strategies.
"""
import asyncio
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any, Set, Type, TypeVar

from src.infrastructure.events.event import Event, EventSource


# Type definitions
EventHandler = Callable[[Event], Any]
IdleHandler = Callable[[], Any]
SchedulerJob = Callable[[], Any]

# Type variable for Event subclasses
E = TypeVar('E', bound=Event)


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

    def push(self, when: datetime, job: SchedulerJob) -> None:
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
        if self._queue and self._queue[0].when <= datetime.now():
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


class RealtimeDispatcher:
    """Event dispatcher for realtime event processing.
    
    This dispatcher supports both event type based and event source based
    subscription models, and provides scheduling capabilities.
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
                
        # Scheduler for timed jobs
        self._scheduler_queue = SchedulerQueue()
        
        # Handlers to call when there are no events to process
        self._idle_handlers: List[IdleHandler] = []
        
        # Running state
        self._running = False
        self._stopped = False
        
        # Logger
        self._logger = logger or logging.getLogger(__name__)

    def subscribe_event_type(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to events of a specific type.
        
        Args:
            event_type: The type of event to subscribe to (string identifier)
            handler: Function to call when an event of this type is published
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        if handler not in self._event_handlers[event_type]:
            self._event_handlers[event_type].append(handler)

    def publish_event(self, event_type: str, event: Event) -> None:
        """Publish an event to all subscribers of the specified type.
        
        Args:
            event_type: The type of event being published
            event: The event object
        """
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
        handlers = self._source_handlers.setdefault(source, [])
        if event_handler not in handlers:
            handlers.append(event_handler)
    
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
        self._stopped = False
        try:
            while not self._stopped:
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
        self._stopped = True

    def _process_scheduled_jobs(self) -> None:
        """Process all scheduled jobs that are ready."""
        while job := self._scheduler_queue.pop():
            try:
                job()
            except Exception as e:
                self._log_error(f"Error executing scheduled job: {e}")

    def _process_source_events(self) -> None:
        """Process events from all sources."""
        for source, handlers in self._source_handlers.items():
            event = source.pop()
            if event:
                for handler in handlers:
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