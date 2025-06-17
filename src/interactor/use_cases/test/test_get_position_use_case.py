"""Tests for GetPositionUseCase."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.interactor.use_cases.get_position_use_case import GetPositionUseCase
from src.interactor.dtos.get_position_dtos import (
    GetPositionInputDto,
    GetPositionOutputDto,
)
from src.interactor.errors.error_classes import ValidationError


class TestGetPositionUseCase:
    """Test cases for GetPositionUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.position_repository = Mock()
        self.position_presenter = Mock()
        
        self.use_case = GetPositionUseCase(
            position_repository=self.position_repository,
            position_presenter=self.position_presenter
        )

    def test_execute_success(self):
        """Test successful position retrieval."""
        # Arrange
        input_dto = GetPositionInputDto()
        
        # Mock position data
        mock_positions = [
            {
                'item_code': 'MXFL2',
                'quantity': 2,
                'average_price': 17500.0,
                'market_value': 35000.0,
                'unrealized_pnl': 500.0,
                'side': 'Long'
            }
        ]
        
        self.position_repository.get_all_positions.return_value = mock_positions
        
        expected_output = GetPositionOutputDto(
            success=True,
            positions=mock_positions,
            total_value=35000.0,
            total_pnl=500.0
        )
        
        self.position_presenter.present.return_value = expected_output
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert result.success is True
        assert result.positions == mock_positions
        assert result.total_value == 35000.0
        assert result.total_pnl == 500.0
        
        self.position_repository.get_all_positions.assert_called_once()
        self.position_presenter.present.assert_called_once()

    def test_execute_empty_positions(self):
        """Test execution with no positions."""
        # Arrange
        input_dto = GetPositionInputDto()
        
        self.position_repository.get_all_positions.return_value = []
        
        expected_output = GetPositionOutputDto(
            success=True,
            positions=[],
            total_value=0.0,
            total_pnl=0.0
        )
        
        self.position_presenter.present.return_value = expected_output
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert result.success is True
        assert result.positions == []
        assert result.total_value == 0.0
        assert result.total_pnl == 0.0

    def test_execute_repository_error(self):
        """Test execution when repository raises error."""
        # Arrange
        input_dto = GetPositionInputDto()
        
        self.position_repository.get_all_positions.side_effect = Exception("Database error")
        
        expected_output = GetPositionOutputDto(
            success=False,
            error_message="Failed to retrieve positions: Database error"
        )
        
        self.position_presenter.present.return_value = expected_output
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert result.success is False
        assert "Database error" in result.error_message

    def test_execute_presenter_error(self):
        """Test execution when presenter raises error."""
        # Arrange
        input_dto = GetPositionInputDto()
        
        mock_positions = [{'item_code': 'MXFL2', 'quantity': 1}]
        self.position_repository.get_all_positions.return_value = mock_positions
        
        self.position_presenter.present.side_effect = Exception("Presentation error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Presentation error"):
            self.use_case.execute(input_dto)

    def test_execute_with_multiple_positions(self):
        """Test execution with multiple positions."""
        # Arrange
        input_dto = GetPositionInputDto()
        
        mock_positions = [
            {
                'item_code': 'MXFL2',
                'quantity': 2,
                'average_price': 17500.0,
                'market_value': 35000.0,
                'unrealized_pnl': 500.0,
                'side': 'Long'
            },
            {
                'item_code': 'TXFL2',
                'quantity': -1,
                'average_price': 18000.0,
                'market_value': -18000.0,
                'unrealized_pnl': -200.0,
                'side': 'Short'
            }
        ]
        
        self.position_repository.get_all_positions.return_value = mock_positions
        
        expected_output = GetPositionOutputDto(
            success=True,
            positions=mock_positions,
            total_value=17000.0,  # 35000 - 18000
            total_pnl=300.0      # 500 - 200
        )
        
        self.position_presenter.present.return_value = expected_output
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert result.success is True
        assert len(result.positions) == 2
        assert result.total_value == 17000.0
        assert result.total_pnl == 300.0

    def test_execute_validates_input_dto(self):
        """Test that execute validates input DTO."""
        # Act & Assert
        with pytest.raises(ValidationError):
            self.use_case.execute(None)

    def test_execute_with_invalid_input_dto(self):
        """Test execution with invalid input DTO."""
        # Arrange
        invalid_input = "not a dto"
        
        # Act & Assert
        with pytest.raises(ValidationError):
            self.use_case.execute(invalid_input)