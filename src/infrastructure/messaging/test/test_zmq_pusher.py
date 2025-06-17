"""Tests for ZMQ Pusher."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import zmq

from src.infrastructure.messaging.zmq_pusher import ZmqPusher
from src.infrastructure.exceptions.communication_exceptions import (
    ConnectionError as CommConnectionError,
    MessageSerializationError,
)


class TestZmqPusher:
    """Test cases for ZmqPusher."""

    def setup_method(self):
        """Set up test fixtures."""
        self.address = "tcp://127.0.0.1:5556"
        self.logger = Mock()

    @patch('zmq.Context')
    def test_init_creates_context_and_socket(self, mock_context):
        """Test initialization creates ZMQ context and socket."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        pusher = ZmqPusher(self.address, self.logger)
        
        mock_context.assert_called_once()
        mock_context_instance.socket.assert_called_once_with(zmq.PUSH)
        assert pusher.address == self.address
        assert pusher.logger == self.logger

    @patch('zmq.Context')
    def test_connect_success(self, mock_context):
        """Test successful connection."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        pusher = ZmqPusher(self.address, self.logger)
        
        # Test connect
        result = pusher.connect()
        
        assert result is True
        mock_socket.connect.assert_called_once_with(self.address)
        self.logger.log_info.assert_called()

    @patch('zmq.Context')
    def test_connect_failure(self, mock_context):
        """Test connection failure."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        mock_socket.connect.side_effect = zmq.ZMQError("Connect failed")
        
        pusher = ZmqPusher(self.address, self.logger)
        
        # Test connect failure
        with pytest.raises(CommConnectionError):
            pusher.connect()

    @patch('zmq.Context')
    def test_push_success(self, mock_context):
        """Test successful message pushing."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        pusher = ZmqPusher(self.address, self.logger)
        pusher._connected = True
        
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.serialize.return_value = b"serialized_data"
        pusher.serializer = mock_serializer
        
        test_data = {"test": "data"}
        
        # Test push
        result = pusher.push(test_data)
        
        assert result is True
        mock_serializer.serialize.assert_called_once_with(test_data)
        mock_socket.send.assert_called_once_with(b"serialized_data")

    @patch('zmq.Context')
    def test_push_without_connection(self, mock_context):
        """Test pushing without connection raises error."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        pusher = ZmqPusher(self.address, self.logger)
        # Don't set _connected = True
        
        test_data = {"test": "data"}
        
        # Test push without connection
        with pytest.raises(CommConnectionError, match="Pusher not connected"):
            pusher.push(test_data)

    @patch('zmq.Context')
    def test_push_serialization_error(self, mock_context):
        """Test pushing with serialization error."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        pusher = ZmqPusher(self.address, self.logger)
        pusher._connected = True
        
        # Mock serializer to raise exception
        mock_serializer = Mock()
        mock_serializer.serialize.side_effect = Exception("Serialization failed")
        pusher.serializer = mock_serializer
        
        test_data = {"test": "data"}
        
        # Test push with serialization error
        with pytest.raises(MessageSerializationError):
            pusher.push(test_data)

    @patch('zmq.Context')
    def test_push_zmq_error(self, mock_context):
        """Test pushing with ZMQ error."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        pusher = ZmqPusher(self.address, self.logger)
        pusher._connected = True
        
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.serialize.return_value = b"serialized_data"
        pusher.serializer = mock_serializer
        
        # Mock socket to raise ZMQ error
        mock_socket.send.side_effect = zmq.ZMQError("Send failed")
        
        test_data = {"test": "data"}
        
        # Test push with ZMQ error
        result = pusher.push(test_data)
        
        assert result is False
        self.logger.log_error.assert_called()

    @patch('zmq.Context')
    def test_close_cleanup(self, mock_context):
        """Test close properly cleans up resources."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        pusher = ZmqPusher(self.address, self.logger)
        pusher._connected = True
        
        # Test close
        pusher.close()
        
        mock_socket.close.assert_called_once()
        mock_context_instance.term.assert_called_once()
        assert pusher._connected is False

    @patch('zmq.Context')
    def test_close_with_exception(self, mock_context):
        """Test close handles exceptions gracefully."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        mock_socket.close.side_effect = Exception("Close failed")
        
        pusher = ZmqPusher(self.address, self.logger)
        
        # Test close with exception
        pusher.close()  # Should not raise exception
        
        self.logger.log_error.assert_called()

    @patch('zmq.Context')
    def test_context_manager(self, mock_context):
        """Test ZmqPusher can be used as context manager."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        # Test context manager
        with ZmqPusher(self.address, self.logger) as pusher:
            assert isinstance(pusher, ZmqPusher)
        
        # Close should be called automatically
        mock_socket.close.assert_called_once()
        mock_context_instance.term.assert_called_once()