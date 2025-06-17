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

    @patch('time.sleep')
    @patch('zmq.Context')
    def test_init_socket_retry_mechanism(self, mock_context, mock_sleep):
        """Test socket initialization retry mechanism."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        # First two bind attempts fail, third succeeds
        mock_socket.bind.side_effect = [
            zmq.ZMQError("Address already in use"),
            zmq.ZMQError("Address already in use"),
            None  # Success on third attempt
        ]
        
        # Test initialization with retries
        publisher = ZmqPublisher(self.address, self.logger, connect_retry_attempts=3)
        
        # Verify bind was called 3 times
        assert mock_socket.bind.call_count == 3
        # Verify sleep was called for retry delays
        assert mock_sleep.call_count >= 2

    @patch('zmq.Context')
    def test_init_socket_all_retries_fail(self, mock_context):
        """Test socket initialization when all retry attempts fail."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        # All bind attempts fail
        mock_socket.bind.side_effect = zmq.ZMQError("Address already in use")
        
        # Test initialization should handle all failed attempts gracefully
        publisher = ZmqPublisher(self.address, self.logger, connect_retry_attempts=2)
        
        # Should have attempted bind twice
        assert mock_socket.bind.call_count == 2
        # Publisher should not be initialized
        assert not hasattr(publisher, '_is_initialized') or not publisher._is_initialized

    @patch('zmq.Context')
    def test_socket_cleanup_during_retry(self, mock_context):
        """Test socket cleanup during retry attempts."""
        mock_context_instance = Mock()
        mock_socket1 = Mock()
        mock_socket2 = Mock()
        mock_context.return_value = mock_context_instance
        
        # Return different socket instances on subsequent calls
        mock_context_instance.socket.side_effect = [mock_socket1, mock_socket2]
        
        # First bind fails, second succeeds
        mock_socket1.bind.side_effect = zmq.ZMQError("Bind failed")
        mock_socket2.bind.return_value = None
        
        # Test initialization
        publisher = ZmqPublisher(self.address, self.logger, connect_retry_attempts=2)
        
        # Verify first socket was closed after failure
        mock_socket1.close.assert_called_once()
        # Verify second socket was used successfully
        mock_socket2.bind.assert_called_once()

    @patch('zmq.Context')
    def test_socket_cleanup_error_handling(self, mock_context):
        """Test error handling during socket cleanup."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        # Socket close raises error
        mock_socket.close.side_effect = zmq.ZMQError("Close failed")
        mock_socket.bind.side_effect = zmq.ZMQError("Bind failed")
        
        # Should handle cleanup error gracefully
        publisher = ZmqPublisher(self.address, self.logger, connect_retry_attempts=1)
        
        # Logger should have recorded the warning
        self.logger.log_warning.assert_called()

    @patch('zmq.Context')
    def test_socket_options_configuration(self, mock_context):
        """Test socket options are properly configured."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        # Test initialization
        publisher = ZmqPublisher(self.address, self.logger)
        
        # Verify socket options were set
        mock_socket.setsockopt.assert_any_call(zmq.LINGER, 0)
        mock_socket.setsockopt.assert_any_call(zmq.SNDHWM, 1000)

    @patch('zmq.Context')
    def test_internal_address_storage(self, mock_context):
        """Test internal address storage."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        publisher = ZmqPublisher(self.address, self.logger)
        
        assert publisher._address == self.address

    @patch('zmq.Context')
    def test_initialization_status(self, mock_context):
        """Test initialization status tracking."""
        mock_context_instance = Mock()
        mock_socket = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.socket.return_value = mock_socket
        
        publisher = ZmqPublisher(self.address, self.logger)
        
        # Should have initialization status
        assert hasattr(publisher, '_is_initialized')

    @patch('zmq.Context')
    def test_custom_context_usage(self, mock_context):
        """Test using custom ZMQ context."""
        custom_context = Mock()
        mock_socket = Mock()
        custom_context.socket.return_value = mock_socket
        
        # Test with custom context
        publisher = ZmqPublisher(self.address, self.logger, context=custom_context)
        
        # Should use provided context, not create new one
        mock_context.instance.assert_not_called()
        custom_context.socket.assert_called_once_with(zmq.PUB)