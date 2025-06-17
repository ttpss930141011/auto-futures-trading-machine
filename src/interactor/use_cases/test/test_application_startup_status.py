"""Tests for ApplicationStartupStatusUseCase."""

import pytest
from unittest.mock import Mock

from src.interactor.use_cases.application_startup_status import (
    ApplicationStartupStatusUseCase,
)


class TestApplicationStartupStatusUseCase:
    """Test cases for ApplicationStartupStatusUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Mock()
        self.status_checker = Mock()
        self.use_case = ApplicationStartupStatusUseCase(
            logger=self.logger, 
            status_checker=self.status_checker
        )

    def test_execute_success_all_services_running(self):
        """Test successful execution when all services are running."""
        # Arrange
        mock_status = {
            'gateway_server': True,
            'market_data_service': True,
            'process_manager': True,
        }
        self.status_checker.get_status_summary.return_value = mock_status
        
        # Act
        result = self.use_case.execute()
        
        # Assert
        assert isinstance(result, dict)
        assert result == mock_status
        self.status_checker.get_status_summary.assert_called_once()
        self.logger.log_info.assert_called()

    def test_execute_some_services_down(self):
        """Test execution when some services are down."""
        # Arrange
        mock_status = {
            'gateway_server': True,
            'market_data_service': False,
            'process_manager': True,
        }
        self.status_checker.get_status_summary.return_value = mock_status
        
        # Act
        result = self.use_case.execute()
        
        # Assert
        assert isinstance(result, dict)
        assert result == mock_status
        assert result['market_data_service'] is False
        self.status_checker.get_status_summary.assert_called_once()
        self.logger.log_warning.assert_called()

    def test_execute_all_services_down(self):
        """Test execution when all services are down."""
        # Arrange
        mock_status = {
            'gateway_server': False,
            'market_data_service': False,
            'process_manager': False,
        }
        self.status_checker.get_status_summary.return_value = mock_status
        
        # Act
        result = self.use_case.execute()
        
        # Assert
        assert isinstance(result, dict)
        assert result == mock_status
        assert all(not status for status in result.values())
        self.status_checker.get_status_summary.assert_called_once()
        self.logger.log_warning.assert_called()

    def test_execute_empty_status(self):
        """Test execution when status checker returns empty status."""
        # Arrange
        mock_status = {}
        self.status_checker.get_status_summary.return_value = mock_status
        
        # Act
        result = self.use_case.execute()
        
        # Assert
        assert isinstance(result, dict)
        assert result == mock_status
        self.status_checker.get_status_summary.assert_called_once()
        self.logger.log_info.assert_called()

    def test_initialization(self):
        """Test use case initialization."""
        logger = Mock()
        status_checker = Mock()
        
        use_case = ApplicationStartupStatusUseCase(
            logger=logger,
            status_checker=status_checker
        )
        
        assert use_case.logger == logger
        assert use_case.status_checker == status_checker