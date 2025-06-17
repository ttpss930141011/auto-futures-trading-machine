"""Tests for ZMQ Puller."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import zmq

from src.infrastructure.messaging.zmq_puller import ZmqPuller
from src.infrastructure.exceptions.communication_exceptions import (
    ConnectionError as CommConnectionError,
    MessageSerializationError,
)


class TestZmqPuller:
    """Test cases for ZmqPuller."""

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
        
        puller = ZmqPuller(self.address, self.logger)
        
        mock_context.assert_called_once()
        mock_context_instance.socket.assert_called_once_with(zmq.PULL)
        assert puller.address == self.address
        assert puller.logger == self.logger

    @patch('zmq.Context')
    def test_connect_success(self, mock_context):
        """Test successful connection."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        puller = ZmqPuller(self.address, self.logger)
        
        # Test connect
        result = puller.connect()
        
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
        
        puller = ZmqPuller(self.address, self.logger)
        
        # Test connect failure
        with pytest.raises(CommConnectionError):
            puller.connect()

    @patch('zmq.Context')
    def test_pull_success(self, mock_context):
        """Test successful message pulling."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        puller = ZmqPuller(self.address, self.logger)
        puller._connected = True
        
        # Mock socket receive
        mock_socket.recv.return_value = b"serialized_data"
        
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.deserialize.return_value = {"test": "data"}
        puller.serializer = mock_serializer
        
        # Test pull
        result = puller.pull()
        
        assert result == {"test": "data"}
        mock_socket.recv.assert_called_once_with(zmq.NOBLOCK)
        mock_serializer.deserialize.assert_called_once_with(b"serialized_data")

    @patch('zmq.Context')
    def test_pull_without_connection(self, mock_context):
        """Test pulling without connection raises error."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        puller = ZmqPuller(self.address, self.logger)
        # Don't set _connected = True
        
        # Test pull without connection
        with pytest.raises(CommConnectionError, match="Puller not connected"):
            puller.pull()

    @patch('zmq.Context')
    def test_pull_no_message(self, mock_context):
        """Test pulling when no message available."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        puller = ZmqPuller(self.address, self.logger)
        puller._connected = True
        
        # Mock socket to raise EAGAIN (no message available)
        mock_socket.recv.side_effect = zmq.Again()
        
        # Test pull with no message
        result = puller.pull()
        
        assert result is None

    @patch('zmq.Context')
    def test_pull_deserialization_error(self, mock_context):
        """Test pulling with deserialization error."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        puller = ZmqPuller(self.address, self.logger)
        puller._connected = True
        
        # Mock socket receive
        mock_socket.recv.return_value = b"invalid_data"
        
        # Mock serializer to raise exception
        mock_serializer = Mock()
        mock_serializer.deserialize.side_effect = Exception("Deserialization failed")
        puller.serializer = mock_serializer
        
        # Test pull with deserialization error
        with pytest.raises(MessageSerializationError):
            puller.pull()

    @patch('zmq.Context')
    def test_pull_blocking_success(self, mock_context):
        """Test successful blocking message pulling."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        puller = ZmqPuller(self.address, self.logger)
        puller._connected = True
        
        # Mock socket receive
        mock_socket.recv.return_value = b"serialized_data"
        
        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.deserialize.return_value = {"test": "data"}
        puller.serializer = mock_serializer
        
        # Test blocking pull
        result = puller.pull_blocking()
        
        assert result == {"test": "data"}
        mock_socket.recv.assert_called_once()  # No NOBLOCK flag
        mock_serializer.deserialize.assert_called_once_with(b"serialized_data")

    @patch('zmq.Context')
    def test_pull_blocking_timeout(self, mock_context):
        """Test blocking pull with timeout."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        puller = ZmqPuller(self.address, self.logger)
        puller._connected = True
        
        # Mock socket to timeout
        mock_socket.recv.side_effect = zmq.Again()
        
        # Test pull with timeout
        result = puller.pull_blocking(timeout_ms=100)
        
        assert result is None
        mock_socket.setsockopt.assert_called_with(zmq.RCVTIMEO, 100)

    @patch('zmq.Context')
    def test_close_cleanup(self, mock_context):
        """Test close properly cleans up resources."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        puller = ZmqPuller(self.address, self.logger)
        puller._connected = True
        
        # Test close
        puller.close()
        
        mock_socket.close.assert_called_once()
        mock_context_instance.term.assert_called_once()
        assert puller._connected is False

    @patch('zmq.Context')
    def test_close_with_exception(self, mock_context):
        """Test close handles exceptions gracefully."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        mock_socket.close.side_effect = Exception("Close failed")
        
        puller = ZmqPuller(self.address, self.logger)
        
        # Test close with exception
        puller.close()  # Should not raise exception
        
        self.logger.log_error.assert_called()

    @patch('zmq.Context')
    def test_context_manager(self, mock_context):
        """Test ZmqPuller can be used as context manager."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        # Test context manager
        with ZmqPuller(self.address, self.logger) as puller:
            assert isinstance(puller, ZmqPuller)
        
        # Close should be called automatically
        mock_socket.close.assert_called_once()
        mock_context_instance.term.assert_called_once()