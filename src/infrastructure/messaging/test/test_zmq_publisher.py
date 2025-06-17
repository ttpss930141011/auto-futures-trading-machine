"""Tests for ZMQ Publisher."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import zmq

from src.infrastructure.messaging.zmq_publisher import ZmqPublisher
from src.infrastructure.exceptions.communication_exceptions import (
    ZMQConnectionException,
    ZMQMessageException,
)


class TestZmqPublisher:
    """Test cases for ZmqPublisher."""

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
        
        publisher = ZmqPublisher(self.address, self.logger)
        
        mock_context.assert_called_once()
        mock_context_instance.socket.assert_called_once_with(zmq.PUB)
        assert publisher.address == self.address
        assert publisher.logger == self.logger

    @patch('zmq.Context')
    def test_connect_success(self, mock_context):
        """Test successful connection."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        publisher = ZmqPublisher(self.address, self.logger)
        
        # Test connect
        result = publisher.connect()
        
        assert result is True
        mock_socket.bind.assert_called_once_with(self.address)
        self.logger.log_info.assert_called()

    @patch('zmq.Context')
    def test_connect_failure(self, mock_context):
        """Test connection failure."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        mock_socket.bind.side_effect = zmq.ZMQError("Bind failed")
        
        publisher = ZmqPublisher(self.address, self.logger)
        
        # Test connect failure
        with pytest.raises(ZMQConnectionException):
            publisher.connect()

    @patch('zmq.Context')
    def test_publish_success(self, mock_context):
        """Test successful message publishing."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        publisher = ZmqPublisher(self.address, self.logger)
        publisher._connected = True
        
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.serialize.return_value = b"serialized_data"
        publisher.serializer = mock_serializer
        
        test_data = {"test": "data"}
        
        # Test publish
        result = publisher.publish(test_data)
        
        assert result is True
        mock_serializer.serialize.assert_called_once_with(test_data)
        mock_socket.send_multipart.assert_called_once()

    @patch('zmq.Context')
    def test_publish_without_connection(self, mock_context):
        """Test publishing without connection raises error."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        publisher = ZmqPublisher(self.address, self.logger)
        # Don't set _connected = True
        
        test_data = {"test": "data"}
        
        # Test publish without connection
        with pytest.raises(ZMQConnectionException, match="Publisher not connected"):
            publisher.publish(test_data)

    @patch('zmq.Context')
    def test_publish_serialization_error(self, mock_context):
        """Test publishing with serialization error."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        publisher = ZmqPublisher(self.address, self.logger)
        publisher._connected = True
        
        # Mock serializer to raise exception
        mock_serializer = Mock()
        mock_serializer.serialize.side_effect = Exception("Serialization failed")
        publisher.serializer = mock_serializer
        
        test_data = {"test": "data"}
        
        # Test publish with serialization error
        with pytest.raises(ZMQMessageException):
            publisher.publish(test_data)

    @patch('zmq.Context')
    def test_close_cleanup(self, mock_context):
        """Test close properly cleans up resources."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        publisher = ZmqPublisher(self.address, self.logger)
        publisher._connected = True
        
        # Test close
        publisher.close()
        
        mock_socket.close.assert_called_once()
        mock_context_instance.term.assert_called_once()
        assert publisher._connected is False

    @patch('zmq.Context')
    def test_close_with_exception(self, mock_context):
        """Test close handles exceptions gracefully."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        mock_socket.close.side_effect = Exception("Close failed")
        
        publisher = ZmqPublisher(self.address, self.logger)
        
        # Test close with exception
        publisher.close()  # Should not raise exception
        
        self.logger.log_error.assert_called()

    @patch('zmq.Context')
    def test_context_manager(self, mock_context):
        """Test ZmqPublisher can be used as context manager."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        # Test context manager
        with ZmqPublisher(self.address, self.logger) as publisher:
            assert isinstance(publisher, ZmqPublisher)
        
        # Close should be called automatically
        mock_socket.close.assert_called_once()
        mock_context_instance.term.assert_called_once()