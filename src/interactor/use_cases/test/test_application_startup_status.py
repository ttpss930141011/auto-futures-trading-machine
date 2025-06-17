"""Tests for ApplicationStartupStatus use case."""

import pytest
from unittest.mock import Mock, MagicMock

from src.interactor.use_cases.application_startup_status import (
    ApplicationStartupStatus,
    ApplicationStartupStatusInputDto,
    ApplicationStartupStatusOutputDto,
)


class TestApplicationStartupStatus:
    """Test cases for ApplicationStartupStatus use case."""

    def setup_method(self):
        """Set up test fixtures."""
        self.status_checker = Mock()
        self.use_case = ApplicationStartupStatus(self.status_checker)

    def test_execute_success_all_services_running(self):
        """Test successful execution when all services are running."""
        # Arrange
        input_dto = ApplicationStartupStatusInputDto()
        
        # Mock status checker to return healthy status
        mock_status = {
            'gateway_server': True,
            'market_data_service': True,
            'process_manager': True,
            'overall_health': True
        }
        self.status_checker.check_application_health.return_value = mock_status
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert isinstance(result, ApplicationStartupStatusOutputDto)
        assert result.success is True
        assert result.gateway_server_status is True
        assert result.market_data_service_status is True
        assert result.process_manager_status is True
        assert result.overall_health is True
        assert result.error_message is None

    def test_execute_success_some_services_down(self):
        """Test execution when some services are down."""
        # Arrange
        input_dto = ApplicationStartupStatusInputDto()
        
        # Mock status checker to return mixed status
        mock_status = {
            'gateway_server': True,
            'market_data_service': False,
            'process_manager': True,
            'overall_health': False
        }
        self.status_checker.check_application_health.return_value = mock_status
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert result.success is True
        assert result.gateway_server_status is True
        assert result.market_data_service_status is False
        assert result.process_manager_status is True
        assert result.overall_health is False

    def test_execute_status_checker_exception(self):
        """Test execution when status checker raises exception."""
        # Arrange
        input_dto = ApplicationStartupStatusInputDto()
        
        self.status_checker.check_application_health.side_effect = Exception("Health check failed")
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert result.success is False
        assert result.error_message == "Failed to check application status: Health check failed"
        assert result.gateway_server_status is False
        assert result.market_data_service_status is False
        assert result.process_manager_status is False
        assert result.overall_health is False

    def test_execute_with_none_input(self):
        """Test execution with None input."""
        # Act
        result = self.use_case.execute(None)
        
        # Assert
        assert result.success is False
        assert "Invalid input" in result.error_message

    def test_execute_with_invalid_input(self):
        """Test execution with invalid input type."""
        # Act
        result = self.use_case.execute("invalid_input")
        
        # Assert
        assert result.success is False
        assert "Invalid input" in result.error_message

    def test_execute_status_checker_returns_none(self):
        """Test execution when status checker returns None."""
        # Arrange
        input_dto = ApplicationStartupStatusInputDto()
        self.status_checker.check_application_health.return_value = None
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert result.success is False
        assert "Invalid status response" in result.error_message

    def test_execute_status_checker_returns_incomplete_data(self):
        """Test execution when status checker returns incomplete data."""
        # Arrange
        input_dto = ApplicationStartupStatusInputDto()
        
        # Mock status checker to return incomplete status
        mock_status = {
            'gateway_server': True,
            # Missing other required fields
        }
        self.status_checker.check_application_health.return_value = mock_status
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert result.success is True
        assert result.gateway_server_status is True
        # Missing fields should default to False
        assert result.market_data_service_status is False
        assert result.process_manager_status is False
        assert result.overall_health is False

    def test_status_dto_creation(self):
        """Test ApplicationStartupStatusInputDto creation."""
        dto = ApplicationStartupStatusInputDto()
        assert isinstance(dto, ApplicationStartupStatusInputDto)

    def test_output_dto_creation_with_success(self):
        """Test ApplicationStartupStatusOutputDto creation with success."""
        output = ApplicationStartupStatusOutputDto(
            success=True,
            gateway_server_status=True,
            market_data_service_status=True,
            process_manager_status=True,
            overall_health=True
        )
        
        assert output.success is True
        assert output.gateway_server_status is True
        assert output.market_data_service_status is True
        assert output.process_manager_status is True
        assert output.overall_health is True
        assert output.error_message is None

    def test_output_dto_creation_with_error(self):
        """Test ApplicationStartupStatusOutputDto creation with error."""
        error_msg = "Test error message"
        output = ApplicationStartupStatusOutputDto(
            success=False,
            error_message=error_msg
        )
        
        assert output.success is False
        assert output.error_message == error_msg
        assert output.gateway_server_status is False
        assert output.market_data_service_status is False
        assert output.process_manager_status is False
        assert output.overall_health is False