"""Communication-related exceptions."""


class CommunicationException(Exception):
    """Base exception for communication errors."""


class ZMQConnectionException(CommunicationException):
    """Exception raised when ZMQ connection fails."""


class ZMQMessageException(CommunicationException):
    """Exception raised when ZMQ message processing fails."""


class SocketCleanupException(CommunicationException):
    """Exception raised during socket cleanup operations."""