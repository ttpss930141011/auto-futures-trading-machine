"""Tests for GetPositionUseCase."""

import pytest
from unittest.mock import Mock

from src.interactor.use_cases.get_position_use_case import GetPositionUseCase
from src.interactor.dtos.get_position_dtos import (
    GetPositionInputDto,
    GetPositionOutputDto,
    PositionDto,
)


class TestGetPositionUseCase:
    """Test cases for GetPositionUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.position_repository = Mock()
        self.position_presenter = Mock()
        self.logger = Mock()
        
        self.use_case = GetPositionUseCase(
            repository=self.position_repository,
            presenter=self.position_presenter,
            logger=self.logger
        )

    def test_execute_success(self):
        """Test successful position retrieval."""
        # Arrange
        input_dto = GetPositionInputDto(
            order_account="TEST_ACCOUNT",
            product_id="MXFL2"
        )
        
        # Mock position data using actual PositionDto structure
        mock_positions = [
            PositionDto(
                investor_account="TEST_ACCOUNT",
                product_id="MXFL2",
                current_long=2,
                current_short=0,
                avg_cost_long=17500.0,
                unrealized_pl=500.0
            )
        ]
        
        self.position_repository.get_positions.return_value = mock_positions
        
        # Mock presenter response as a dictionary (as shown in actual use case)
        expected_presenter_output = {
            'positions': [pos.to_dict() for pos in mock_positions],
            'total_positions': 1
        }
        
        self.position_presenter.present.return_value = expected_presenter_output
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert isinstance(result, dict)
        assert 'positions' in result
        assert result['total_positions'] == 1
        
        self.position_repository.get_positions.assert_called_once_with(
            input_dto.order_account, input_dto.product_id
        )
        self.position_presenter.present.assert_called_once()

    def test_execute_empty_positions(self):
        """Test execution with no positions."""
        # Arrange
        input_dto = GetPositionInputDto(
            order_account="TEST_ACCOUNT",
            product_id=""  # All products
        )
        
        self.position_repository.get_positions.return_value = []
        
        expected_presenter_output = {
            'positions': [],
            'total_positions': 0
        }
        
        self.position_presenter.present.return_value = expected_presenter_output
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert isinstance(result, dict)
        assert result['positions'] == []
        assert result['total_positions'] == 0
        
        self.position_repository.get_positions.assert_called_once_with(
            input_dto.order_account, input_dto.product_id
        )

    def test_execute_repository_error(self):
        """Test execution when repository raises error."""
        # Arrange
        input_dto = GetPositionInputDto(
            order_account="TEST_ACCOUNT",
            product_id="MXFL2"
        )
        
        self.position_repository.get_positions.side_effect = Exception("Database error")
        
        expected_presenter_output = {
            'error': 'Database error',
            'positions': []
        }
        
        self.position_presenter.present.return_value = expected_presenter_output
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert isinstance(result, dict)
        assert 'error' in result
        assert result['error'] == 'Database error'
        
        self.logger.log_error.assert_called()

    def test_execute_with_multiple_positions(self):
        """Test execution with multiple positions."""
        # Arrange
        input_dto = GetPositionInputDto(
            order_account="TEST_ACCOUNT",
            product_id=""  # All products
        )
        
        mock_positions = [
            PositionDto(
                investor_account="TEST_ACCOUNT",
                product_id="MXFL2",
                current_long=2,
                current_short=0,
                avg_cost_long=17500.0,
                unrealized_pl=500.0
            ),
            PositionDto(
                investor_account="TEST_ACCOUNT",
                product_id="TXFL2",
                current_long=0,
                current_short=1,
                avg_cost_short=18000.0,
                unrealized_pl=-200.0
            )
        ]
        
        self.position_repository.get_positions.return_value = mock_positions
        
        expected_presenter_output = {
            'positions': [pos.to_dict() for pos in mock_positions],
            'total_positions': 2
        }
        
        self.position_presenter.present.return_value = expected_presenter_output
        
        # Act
        result = self.use_case.execute(input_dto)
        
        # Assert
        assert isinstance(result, dict)
        assert result['total_positions'] == 2
        assert len(result['positions']) == 2

    def test_initialization(self):
        """Test use case initialization."""
        repository = Mock()
        presenter = Mock()
        logger = Mock()
        
        use_case = GetPositionUseCase(
            repository=repository,
            presenter=presenter,
            logger=logger
        )
        
        assert use_case._repository == repository
        assert use_case._presenter == presenter
        assert use_case._logger == logger

    def test_input_dto_validation(self):
        """Test input DTO validation."""
        # Valid input
        valid_input = GetPositionInputDto(
            order_account="TEST_ACCOUNT",
            product_id="MXFL2"
        )
        assert valid_input.order_account == "TEST_ACCOUNT"
        assert valid_input.product_id == "MXFL2"
        
        # Invalid input - empty account
        with pytest.raises(ValueError, match="order_account cannot be empty"):
            GetPositionInputDto(order_account="", product_id="MXFL2")

    def test_position_dto_properties(self):
        """Test PositionDto properties and methods."""
        position = PositionDto(
            investor_account="TEST_ACCOUNT",
            product_id="MXFL2",
            current_long=3,
            current_short=1
        )
        
        assert position.net_position == 2  # 3 - 1
        assert position.has_position is True
        
        # Test to_dict method
        position_dict = position.to_dict()
        assert isinstance(position_dict, dict)
        assert position_dict['investor_account'] == "TEST_ACCOUNT"
        assert position_dict['net_position'] == 2