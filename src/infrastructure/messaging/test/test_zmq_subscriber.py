"""Tests for ZMQ Subscriber."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import zmq

from src.infrastructure.messaging.zmq_subscriber import ZmqSubscriber
from src.infrastructure.exceptions.communication_exceptions import (
    ConnectionError as CommConnectionError,
    MessageSerializationError,
)


class TestZmqSubscriber:
    """Test cases for ZmqSubscriber."""

    def setup_method(self):
        """Set up test fixtures."""
        self.address = "tcp://127.0.0.1:5555"
        self.logger = Mock()

    @patch('zmq.Context')
    def test_init_creates_context_and_socket(self, mock_context):
        """Test initialization creates ZMQ context and socket."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        subscriber = ZmqSubscriber(self.address, self.logger)
        
        mock_context.assert_called_once()
        mock_context_instance.socket.assert_called_once_with(zmq.SUB)
        assert subscriber.address == self.address
        assert subscriber.logger == self.logger

    @patch('zmq.Context')
    def test_connect_success(self, mock_context):
        """Test successful connection."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        subscriber = ZmqSubscriber(self.address, self.logger)
        
        # Test connect
        result = subscriber.connect()
        
        assert result is True
        mock_socket.connect.assert_called_once_with(self.address)
        mock_socket.setsockopt.assert_called_once_with(zmq.SUBSCRIBE, b"")
        self.logger.log_info.assert_called()

    @patch('zmq.Context')
    def test_connect_failure(self, mock_context):
        """Test connection failure."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        mock_socket.connect.side_effect = zmq.ZMQError("Connect failed")
        
        subscriber = ZmqSubscriber(self.address, self.logger)
        
        # Test connect failure
        with pytest.raises(CommConnectionError):
            subscriber.connect()

    @patch('zmq.Context')
    def test_receive_success(self, mock_context):
        """Test successful message receiving."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        subscriber = ZmqSubscriber(self.address, self.logger)
        subscriber._connected = True
        
        # Mock socket receive
        mock_socket.recv_multipart.return_value = [b"topic", b"serialized_data"]
        
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.deserialize.return_value = {"test": "data"}
        subscriber.serializer = mock_serializer
        
        # Test receive
        result = subscriber.receive()
        
        assert result == {"test": "data"}
        mock_socket.recv_multipart.assert_called_once_with(zmq.NOBLOCK)
        mock_serializer.deserialize.assert_called_once_with(b"serialized_data")

    @patch('zmq.Context')
    def test_receive_without_connection(self, mock_context):
        """Test receiving without connection raises error."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        subscriber = ZmqSubscriber(self.address, self.logger)
        # Don't set _connected = True
        
        # Test receive without connection
        with pytest.raises(CommConnectionError, match="Subscriber not connected"):
            subscriber.receive()

    @patch('zmq.Context')
    def test_receive_no_message(self, mock_context):
        """Test receiving when no message available."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        subscriber = ZmqSubscriber(self.address, self.logger)
        subscriber._connected = True
        
        # Mock socket to raise EAGAIN (no message available)
        mock_socket.recv_multipart.side_effect = zmq.Again()
        
        # Test receive with no message
        result = subscriber.receive()
        
        assert result is None

    @patch('zmq.Context')
    def test_receive_deserialization_error(self, mock_context):
        """Test receiving with deserialization error."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        subscriber = ZmqSubscriber(self.address, self.logger)
        subscriber._connected = True
        
        # Mock socket receive
        mock_socket.recv_multipart.return_value = [b"topic", b"invalid_data"]
        
        # Mock serializer to raise exception
        mock_serializer = Mock()
        mock_serializer.deserialize.side_effect = Exception("Deserialization failed")
        subscriber.serializer = mock_serializer
        
        # Test receive with deserialization error
        with pytest.raises(MessageSerializationError):
            subscriber.receive()

    @patch('zmq.Context')
    def test_close_cleanup(self, mock_context):
        """Test close properly cleans up resources."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        subscriber = ZmqSubscriber(self.address, self.logger)
        subscriber._connected = True
        
        # Test close
        subscriber.close()
        
        mock_socket.close.assert_called_once()
        mock_context_instance.term.assert_called_once()
        assert subscriber._connected is False

    @patch('zmq.Context')
    def test_close_with_exception(self, mock_context):
        """Test close handles exceptions gracefully."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        mock_socket.close.side_effect = Exception("Close failed")
        
        subscriber = ZmqSubscriber(self.address, self.logger)
        
        # Test close with exception
        subscriber.close()  # Should not raise exception
        
        self.logger.log_error.assert_called()

    @patch('zmq.Context')
    def test_context_manager(self, mock_context):
        """Test ZmqSubscriber can be used as context manager."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        # Test context manager
        with ZmqSubscriber(self.address, self.logger) as subscriber:
            assert isinstance(subscriber, ZmqSubscriber)
        
        # Close should be called automatically
        mock_socket.close.assert_called_once()
        mock_context_instance.term.assert_called_once()