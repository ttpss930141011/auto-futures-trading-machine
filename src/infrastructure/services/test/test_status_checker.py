"""Tests for StatusChecker."""

import pytest
from unittest.mock import Mock, MagicMock

from src.infrastructure.services.status_checker import StatusChecker


class TestStatusChecker:
    """Test cases for StatusChecker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service_container = Mock()

    def test_status_checker_initialization(self):
        """Test StatusChecker initializes with service container."""
        checker = StatusChecker(self.service_container)
        assert checker.service_container == self.service_container

    def test_check_logger_status_success(self):
        """Test successful logger status check."""
        # Arrange
        mock_logger = Mock()
        self.service_container.logger = mock_logger
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_logger_status()
        
        # Assert
        assert result is True

    def test_check_logger_status_none_logger(self):
        """Test logger status check when logger is None."""
        # Arrange
        self.service_container.logger = None
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_logger_status()
        
        # Assert
        assert result is False

    def test_check_config_status_success(self):
        """Test successful config status check."""
        # Arrange
        mock_config = Mock()
        self.service_container.config = mock_config
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_config_status()
        
        # Assert
        assert result is True

    def test_check_config_status_none_config(self):
        """Test config status check when config is None."""
        # Arrange
        self.service_container.config = None
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_config_status()
        
        # Assert
        assert result is False

    def test_check_session_repository_status_success(self):
        """Test successful session repository status check."""
        # Arrange
        mock_session_repo = Mock()
        self.service_container.session_repository = mock_session_repo
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_session_repository_status()
        
        # Assert
        assert result is True

    def test_check_session_repository_status_none_repository(self):
        """Test session repository status check when repository is None."""
        # Arrange
        self.service_container.session_repository = None
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_session_repository_status()
        
        # Assert
        assert result is False

    def test_check_condition_repository_status_success(self):
        """Test successful condition repository status check."""
        # Arrange
        mock_condition_repo = Mock()
        self.service_container.condition_repository = mock_condition_repo
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_condition_repository_status()
        
        # Assert
        assert result is True

    def test_check_condition_repository_status_none_repository(self):
        """Test condition repository status check when repository is None."""
        # Arrange
        self.service_container.condition_repository = None
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_condition_repository_status()
        
        # Assert
        assert result is False

    def test_check_exchange_api_status_success(self):
        """Test successful exchange API status check."""
        # Arrange
        mock_exchange_api = Mock()
        self.service_container.exchange_api = mock_exchange_api
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_exchange_api_status()
        
        # Assert
        assert result is True

    def test_check_exchange_api_status_none_api(self):
        """Test exchange API status check when API is None."""
        # Arrange
        self.service_container.exchange_api = None
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_exchange_api_status()
        
        # Assert
        assert result is False

    def test_check_all_services_all_healthy(self):
        """Test check_all_services when all services are healthy."""
        # Arrange
        self.service_container.logger = Mock()
        self.service_container.config = Mock()
        self.service_container.session_repository = Mock()
        self.service_container.condition_repository = Mock()
        self.service_container.exchange_api = Mock()
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_all_services()
        
        # Assert
        expected = {
            'logger': True,
            'config': True,
            'session_repository': True,
            'condition_repository': True,
            'exchange_api': True,
            'overall_health': True
        }
        assert result == expected

    def test_check_all_services_some_unhealthy(self):
        """Test check_all_services when some services are unhealthy."""
        # Arrange
        self.service_container.logger = Mock()
        self.service_container.config = None  # Unhealthy
        self.service_container.session_repository = Mock()
        self.service_container.condition_repository = None  # Unhealthy
        self.service_container.exchange_api = Mock()
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_all_services()
        
        # Assert
        expected = {
            'logger': True,
            'config': False,
            'session_repository': True,
            'condition_repository': False,
            'exchange_api': True,
            'overall_health': False
        }
        assert result == expected

    def test_check_all_services_all_unhealthy(self):
        """Test check_all_services when all services are unhealthy."""
        # Arrange
        self.service_container.logger = None
        self.service_container.config = None
        self.service_container.session_repository = None
        self.service_container.condition_repository = None
        self.service_container.exchange_api = None
        
        checker = StatusChecker(self.service_container)
        
        # Act
        result = checker.check_all_services()
        
        # Assert
        expected = {
            'logger': False,
            'config': False,
            'session_repository': False,
            'condition_repository': False,
            'exchange_api': False,
            'overall_health': False
        }
        assert result == expected

    def test_status_checker_with_none_service_container(self):
        """Test StatusChecker behavior with None service container."""
        checker = StatusChecker(None)
        
        # All status checks should return False
        assert checker.check_logger_status() is False
        assert checker.check_config_status() is False
        assert checker.check_session_repository_status() is False
        assert checker.check_condition_repository_status() is False
        assert checker.check_exchange_api_status() is False
        
        result = checker.check_all_services()
        expected = {
            'logger': False,
            'config': False,
            'session_repository': False,
            'condition_repository': False,
            'exchange_api': False,
            'overall_health': False
        }
        assert result == expected