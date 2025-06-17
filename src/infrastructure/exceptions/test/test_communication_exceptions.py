"""Tests for communication exceptions."""

import pytest

from src.infrastructure.exceptions.communication_exceptions import (
    CommunicationException,
    ZMQConnectionException,
    ZMQMessageException,
    SocketCleanupException,
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


class TestZMQConnectionException:
    """Test cases for ZMQConnectionException."""

    def test_zmq_connection_exception_creation(self):
        """Test ZMQConnectionException can be created with message."""
        message = "ZMQ connection failed"
        error = ZMQConnectionException(message)
        
        assert str(error) == message
        assert isinstance(error, CommunicationException)

    def test_zmq_connection_exception_inheritance(self):
        """Test ZMQConnectionException inherits from CommunicationException."""
        error = ZMQConnectionException("test")
        assert isinstance(error, CommunicationException)
        assert isinstance(error, Exception)


class TestZMQMessageException:
    """Test cases for ZMQMessageException."""

    def test_zmq_message_exception_creation(self):
        """Test ZMQMessageException can be created with message."""
        message = "ZMQ message processing failed"
        error = ZMQMessageException(message)
        
        assert str(error) == message
        assert isinstance(error, CommunicationException)

    def test_zmq_message_exception_inheritance(self):
        """Test ZMQMessageException inherits from CommunicationException."""
        error = ZMQMessageException("test")
        assert isinstance(error, CommunicationException)
        assert isinstance(error, Exception)


class TestSocketCleanupException:
    """Test cases for SocketCleanupException."""

    def test_socket_cleanup_exception_creation(self):
        """Test SocketCleanupException can be created with message."""
        message = "Socket cleanup failed"
        error = SocketCleanupException(message)
        
        assert str(error) == message
        assert isinstance(error, CommunicationException)

    def test_socket_cleanup_exception_inheritance(self):
        """Test SocketCleanupException inherits from CommunicationException."""
        error = SocketCleanupException("test")
        assert isinstance(error, CommunicationException)
        assert isinstance(error, Exception)