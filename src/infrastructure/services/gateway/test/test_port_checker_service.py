"""Tests for Port Checker Service."""

import pytest
import socket
from unittest.mock import Mock, patch, MagicMock, call
from contextlib import closing

from src.infrastructure.services.gateway.port_checker_service import PortCheckerService


class TestPortCheckerService:
    """Test cases for PortCheckerService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.ZMQ_TICK_PORT = 5555
        self.mock_config.ZMQ_SIGNAL_PORT = 5556
        
        self.mock_logger = Mock()

    def test_initialization(self):
        """Test service initialization."""
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        assert service.config == self.mock_config
        assert service.logger == self.mock_logger

    @patch('socket.socket')
    def test_check_port_availability_all_available(self, mock_socket):
        """Test port availability check when all ports are available."""
        # Mock socket to simulate successful binding
        mock_sock_instance = Mock()
        mock_socket.return_value.__enter__ = Mock(return_value=mock_sock_instance)
        mock_socket.return_value.__exit__ = Mock(return_value=False)
        mock_sock_instance.bind.return_value = None  # Successful bind
        
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        result = service.check_port_availability()
        
        # Should return all ports as available
        expected_result = {5555: True, 5556: True}
        assert result == expected_result
        
        # Verify sockets were created correctly
        assert mock_socket.call_count == 2
        mock_socket.assert_has_calls([
            call(socket.AF_INET, socket.SOCK_STREAM),
            call(socket.AF_INET, socket.SOCK_STREAM)
        ])
        
        # Verify bind was called for both ports
        assert mock_sock_instance.bind.call_count == 2
        mock_sock_instance.bind.assert_has_calls([
            call(("127.0.0.1", 5555)),
            call(("127.0.0.1", 5556))
        ])
        
        # Verify logging
        assert self.mock_logger.log_info.call_count == 2

    @patch('socket.socket')
    def test_check_port_availability_all_in_use(self, mock_socket):
        """Test port availability check when all ports are in use."""
        # Mock socket to simulate failed binding
        mock_sock_instance = Mock()
        mock_socket.return_value.__enter__ = Mock(return_value=mock_sock_instance)
        mock_socket.return_value.__exit__ = Mock(return_value=False)
        mock_sock_instance.bind.side_effect = socket.error("Address already in use")
        
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        result = service.check_port_availability()
        
        # Should return all ports as unavailable
        expected_result = {5555: False, 5556: False}
        assert result == expected_result
        
        # Verify error logging
        assert self.mock_logger.log_error.call_count == 2

    @patch('socket.socket')
    def test_check_port_availability_mixed(self, mock_socket):
        """Test port availability check with mixed availability."""
        # Mock socket to simulate mixed results
        mock_sock_instance = Mock()
        mock_socket.return_value.__enter__ = Mock(return_value=mock_sock_instance)
        mock_socket.return_value.__exit__ = Mock(return_value=False)
        
        # First port available, second port in use
        mock_sock_instance.bind.side_effect = [
            None,  # First bind succeeds
            socket.error("Address already in use")  # Second bind fails
        ]
        
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        result = service.check_port_availability()
        
        # Should return mixed results
        expected_result = {5555: True, 5556: False}
        assert result == expected_result
        
        # Verify appropriate logging
        self.mock_logger.log_info.assert_called_once()
        self.mock_logger.log_error.assert_called_once()

    @patch('socket.socket')
    def test_socket_options_set_correctly(self, mock_socket):
        """Test that socket options are set correctly."""
        mock_sock_instance = Mock()
        mock_socket.return_value.__enter__ = Mock(return_value=mock_sock_instance)
        mock_socket.return_value.__exit__ = Mock(return_value=False)
        mock_sock_instance.bind.return_value = None
        
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        service.check_port_availability()
        
        # Verify SO_REUSEADDR was set
        assert mock_sock_instance.setsockopt.call_count == 2
        mock_sock_instance.setsockopt.assert_has_calls([
            call(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1),
            call(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ])

    def test_port_configuration_access(self):
        """Test that service accesses correct port configuration."""
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        # Should be able to access config ports
        assert hasattr(service.config, 'ZMQ_TICK_PORT')
        assert hasattr(service.config, 'ZMQ_SIGNAL_PORT')
        assert service.config.ZMQ_TICK_PORT == 5555
        assert service.config.ZMQ_SIGNAL_PORT == 5556

    @patch('socket.socket')
    def test_socket_context_manager(self, mock_socket):
        """Test that sockets are properly managed with context manager."""
        mock_sock_instance = Mock()
        mock_socket.return_value.__enter__ = Mock(return_value=mock_sock_instance)
        mock_socket.return_value.__exit__ = Mock(return_value=False)
        mock_sock_instance.bind.return_value = None
        
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        service.check_port_availability()
        
        # Verify context manager was used correctly
        assert mock_socket.return_value.__enter__.call_count == 2
        assert mock_socket.return_value.__exit__.call_count == 2

    @patch('socket.socket')
    def test_different_socket_errors(self, mock_socket):
        """Test handling of different socket error types."""
        mock_sock_instance = Mock()
        mock_socket.return_value.__enter__ = Mock(return_value=mock_sock_instance)
        mock_socket.return_value.__exit__ = Mock(return_value=False)
        
        # Different error types
        mock_sock_instance.bind.side_effect = [
            OSError("Permission denied"),  # Different error type
            socket.error("Connection refused")  # Another error type
        ]
        
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        result = service.check_port_availability()
        
        # Should handle all socket errors the same way
        expected_result = {5555: False, 5556: False}
        assert result == expected_result
        
        # Should log errors
        assert self.mock_logger.log_error.call_count == 2

    def test_config_dependency_injection(self):
        """Test that config is properly injected."""
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        assert service.config is self.mock_config
        assert service.logger is self.mock_logger

    @patch('socket.socket')
    def test_empty_port_list_handling(self, mock_socket):
        """Test behavior with modified config (edge case)."""
        # Modify config to have same port numbers (edge case)
        self.mock_config.ZMQ_TICK_PORT = 5555
        self.mock_config.ZMQ_SIGNAL_PORT = 5555
        
        mock_sock_instance = Mock()
        mock_socket.return_value.__enter__ = Mock(return_value=mock_sock_instance)
        mock_socket.return_value.__exit__ = Mock(return_value=False)
        mock_sock_instance.bind.return_value = None
        
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        result = service.check_port_availability()
        
        # Should handle duplicate ports correctly
        assert 5555 in result
        assert isinstance(result[5555], bool)

    @patch('socket.socket')
    def test_large_port_numbers(self, mock_socket):
        """Test with large port numbers."""
        # Test with large port numbers
        self.mock_config.ZMQ_TICK_PORT = 65000
        self.mock_config.ZMQ_SIGNAL_PORT = 65001
        
        mock_sock_instance = Mock()
        mock_socket.return_value.__enter__ = Mock(return_value=mock_sock_instance)
        mock_socket.return_value.__exit__ = Mock(return_value=False)
        mock_sock_instance.bind.return_value = None
        
        service = PortCheckerService(self.mock_config, self.mock_logger)
        
        result = service.check_port_availability()
        
        # Should handle large port numbers
        expected_result = {65000: True, 65001: True}
        assert result == expected_result
        
        # Verify correct ports were checked
        mock_sock_instance.bind.assert_has_calls([
            call(("127.0.0.1", 65000)),
            call(("127.0.0.1", 65001))
        ])