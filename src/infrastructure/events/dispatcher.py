import abc
import asyncio
from datetime import datetime
from typing import List, Callable, Awaitable, Any, Dict, Optional
from src.infrastructure.events.event import Event, EventSource
import heapq

EventHandler = Callable[[Event], Awaitable[Any]]
IdleHandler = Callable[[], Awaitable[Any]]
SchedulerJob = Callable[[], Awaitable[Any]]


class EventDispatcher(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def subscribe(self, source: EventSource, event_handler: EventHandler):
        pass

    @abc.abstractmethod
    async def run(self):
        pass

    @abc.abstractmethod
    async def stop(self):
        pass


class ScheduledJob:
    def __init__(self, when: datetime, job: SchedulerJob):
        self.when = when
        self.job = job

    def __lt__(self, other):
        return self.when < other.when


class SchedulerQueue:
    def __init__(self):
        self._queue = []

    def push(self, when: datetime, job: SchedulerJob):
        heapq.heappush(self._queue, ScheduledJob(when, job))

    def pop(self) -> Optional[SchedulerJob]:
        if self._queue and self._queue[0].when <= datetime.utcnow():
            return heapq.heappop(self._queue).job
        return None

    def peek(self) -> Optional[datetime]:
        if self._queue:
            return self._queue[0].when
        return None


class RealtimeDispatcher:
    def __init__(self):
        self._event_handlers: Dict[EventSource, List[EventHandler]] = {}
        self._scheduler_queue = SchedulerQueue()
        self._idle_handlers: List[IdleHandler] = []
        self._running = False

    def now(self) -> datetime:
        return datetime.utcnow()

    # def subscribe(self, event_type: str, handler: EventHandler):
    #     if event_type not in self._event_handlers:
    #         self._event_handlers[event_type] = []
    #     self._event_handlers[event_type].append(handler)
    def subscribe(self, source: EventSource, event_handler: EventHandler):
        assert not self._running, "Subscribing once we're running is not currently supported."

        handlers = self._event_handlers.setdefault(source, [])
        if event_handler not in handlers:
            handlers.append(event_handler)

    def schedule(self, when: datetime, job: SchedulerJob):
        self._scheduler_queue.push(when, job)

    def subscribe_idle(self, handler: IdleHandler):
        self._idle_handlers.append(handler)

    async def run(self):
        self._running = True
        while self._running:
            # now = self.now()

            # Execute scheduled jobs
            while job := self._scheduler_queue.pop():
                await job()

            # Call idle handlers if no events are pending
            if not self._scheduler_queue.peek():
                await self._on_idle()

            await asyncio.sleep(0.01)

    async def stop(self):
        self._running = False

    async def _on_idle(self):
        if self._idle_handlers:
            await asyncio.gather(*[handler() for handler in self._idle_handlers])
        else:
            await asyncio.sleep(0.1)
