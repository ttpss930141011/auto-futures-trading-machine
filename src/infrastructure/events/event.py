"""Event system base classes for futures trading machine.

This module defines the core abstractions for the event-driven architecture:
- Event: Base class for all events
"""
from abc import ABCMeta, abstractmethod
from datetime import datetime


class Event:
    """Base class for events in the system.

    An event is something that occurs at a specific point in time.

    Args:
        when: The datetime when the event occurred.
    """
    def __init__(self, when: datetime):
        self.when: datetime = when
