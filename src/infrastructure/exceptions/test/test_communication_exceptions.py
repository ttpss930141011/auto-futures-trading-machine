"""Tests for communication exceptions."""

import pytest

from src.infrastructure.exceptions.communication_exceptions import (
    CommunicationException,
    ConnectionError,
    MessageSerializationError,
    TimeoutError,
)


class TestCommunicationException:
    """Test cases for CommunicationException base class."""

    def test_communication_exception_creation(self):
        """Test CommunicationException can be created with message."""
        message = "Communication error"
        exception = CommunicationException(message)
        
        assert str(exception) == message
        assert isinstance(exception, Exception)

    def test_communication_exception_inheritance(self):
        """Test CommunicationException inherits from Exception."""
        exception = CommunicationException("test")
        assert isinstance(exception, Exception)


class TestConnectionError:
    """Test cases for ConnectionError."""

    def test_connection_error_creation(self):
        """Test ConnectionError can be created with message."""
        message = "Connection failed"
        error = ConnectionError(message)
        
        assert str(error) == message
        assert isinstance(error, CommunicationException)

    def test_connection_error_inheritance(self):
        """Test ConnectionError inherits from CommunicationException."""
        error = ConnectionError("test")
        assert isinstance(error, CommunicationException)
        assert isinstance(error, Exception)


class TestMessageSerializationError:
    """Test cases for MessageSerializationError."""

    def test_message_serialization_error_creation(self):
        """Test MessageSerializationError can be created with message."""
        message = "Serialization failed"
        error = MessageSerializationError(message)
        
        assert str(error) == message
        assert isinstance(error, CommunicationException)

    def test_message_serialization_error_inheritance(self):
        """Test MessageSerializationError inherits from CommunicationException."""
        error = MessageSerializationError("test")
        assert isinstance(error, CommunicationException)
        assert isinstance(error, Exception)


class TestTimeoutError:
    """Test cases for TimeoutError."""

    def test_timeout_error_creation(self):
        """Test TimeoutError can be created with message."""
        message = "Operation timed out"
        error = TimeoutError(message)
        
        assert str(error) == message
        assert isinstance(error, CommunicationException)

    def test_timeout_error_inheritance(self):
        """Test TimeoutError inherits from CommunicationException."""
        error = TimeoutError("test")
        assert isinstance(error, CommunicationException)
        assert isinstance(error, Exception)