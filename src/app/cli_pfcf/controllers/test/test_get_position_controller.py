"""Tests for Get Position Controller."""

import pytest
from unittest.mock import Mock, patch, call
from io import StringIO

from src.app.cli_pfcf.controllers.get_position_controller import GetPositionController
from src.interactor.dtos.get_position_dtos import GetPositionInputDto


class TestGetPositionController:
    """Test cases for GetPositionController."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_service_container = Mock()
        self.mock_logger = Mock()
        self.mock_session_repository = Mock()
        self.mock_exchange_client = Mock()
        
        # Setup service container
        self.mock_service_container.logger = self.mock_logger
        self.mock_service_container.session_repository = self.mock_session_repository
        self.mock_service_container.exchange_client = self.mock_exchange_client

    def test_initialization(self):
        """Test controller initialization."""
        controller = GetPositionController(self.mock_service_container)
        
        assert controller.service_container == self.mock_service_container
        assert controller.logger == self.mock_logger
        assert controller.session_repository == self.mock_session_repository

    @patch('builtins.input', return_value='TX')
    def test_get_user_input(self, mock_input):
        """Test getting user input."""
        # Setup session repository
        self.mock_session_repository.get_order_account.return_value = "TEST_ACCOUNT"
        
        controller = GetPositionController(self.mock_service_container)
        
        with patch('builtins.print') as mock_print:
            result = controller._get_user_input()
        
        # Verify result
        assert isinstance(result, GetPositionInputDto)
        assert result.order_account == "TEST_ACCOUNT"
        assert result.product_id == "TX"
        
        # Verify interactions
        self.mock_session_repository.get_order_account.assert_called_once()
        mock_input.assert_called_once_with("Enter product id (leave blank for all): ")
        mock_print.assert_called_once_with("Account: TEST_ACCOUNT")

    @patch('builtins.input', return_value='')
    def test_get_user_input_empty_product_id(self, mock_input):
        """Test getting user input with empty product ID."""
        self.mock_session_repository.get_order_account.return_value = "TEST_ACCOUNT"
        
        controller = GetPositionController(self.mock_service_container)
        
        with patch('builtins.print'):
            result = controller._get_user_input()
        
        assert result.product_id == ""

    def test_execute_user_not_logged_in(self):
        """Test execute when user is not logged in."""
        self.mock_session_repository.is_user_logged_in.return_value = False
        
        controller = GetPositionController(self.mock_service_container)
        
        # Execute should return early
        controller.execute()
        
        # Verify logging and early return
        self.mock_session_repository.is_user_logged_in.assert_called_once()
        self.mock_logger.log_info.assert_called_once_with("User not logged in")

    @patch('src.app.cli_pfcf.controllers.get_position_controller.GetPositionUseCase')
    @patch('src.app.cli_pfcf.controllers.get_position_controller.GetPositionPresenter')
    @patch('src.app.cli_pfcf.controllers.get_position_controller.PFCFPositionRepository')
    @patch('builtins.input', return_value='TX')
    def test_execute_success(self, mock_input, mock_repository_class, mock_presenter_class, mock_use_case_class):
        """Test successful execution."""
        # Setup mocks
        self.mock_session_repository.is_user_logged_in.return_value = True
        self.mock_session_repository.get_order_account.return_value = "TEST_ACCOUNT"
        
        mock_repository = Mock()
        mock_presenter = Mock()
        mock_use_case = Mock()
        mock_use_case.execute.return_value = {"status": "success", "positions": []}
        
        mock_repository_class.return_value = mock_repository
        mock_presenter_class.return_value = mock_presenter
        mock_use_case_class.return_value = mock_use_case
        
        controller = GetPositionController(self.mock_service_container)
        
        with patch('builtins.print') as mock_print:
            controller.execute()
        
        # Verify repository creation
        mock_repository_class.assert_called_once_with(client=self.mock_exchange_client)
        
        # Verify presenter creation
        mock_presenter_class.assert_called_once()
        
        # Verify use case creation
        mock_use_case_class.assert_called_once_with(mock_repository, mock_presenter, self.mock_logger)
        
        # Verify use case execution
        mock_use_case.execute.assert_called_once()
        
        # Verify result was printed
        mock_print.assert_called_with({"status": "success", "positions": []})

    @patch('src.app.cli_pfcf.controllers.get_position_controller.GetPositionUseCase')
    @patch('src.app.cli_pfcf.controllers.get_position_controller.GetPositionPresenter')
    @patch('src.app.cli_pfcf.controllers.get_position_controller.PFCFPositionRepository')
    @patch('builtins.input', return_value='')
    def test_execute_with_empty_product_id(self, mock_input, mock_repository_class, mock_presenter_class, mock_use_case_class):
        """Test execution with empty product ID."""
        # Setup mocks
        self.mock_session_repository.is_user_logged_in.return_value = True
        self.mock_session_repository.get_order_account.return_value = "TEST_ACCOUNT"
        
        mock_repository = Mock()
        mock_presenter = Mock()
        mock_use_case = Mock()
        mock_use_case.execute.return_value = {"status": "success", "positions": []}
        
        mock_repository_class.return_value = mock_repository
        mock_presenter_class.return_value = mock_presenter
        mock_use_case_class.return_value = mock_use_case
        
        controller = GetPositionController(self.mock_service_container)
        
        with patch('builtins.print') as mock_print:
            controller.execute()
        
        # Verify input DTO was created with empty product_id
        call_args = mock_use_case.execute.call_args[0][0]
        assert call_args.product_id == ""

    @patch('src.app.cli_pfcf.controllers.get_position_controller.GetPositionUseCase')
    @patch('src.app.cli_pfcf.controllers.get_position_controller.GetPositionPresenter')
    @patch('src.app.cli_pfcf.controllers.get_position_controller.PFCFPositionRepository')
    @patch('builtins.input', return_value='MTX')
    def test_execute_with_specific_product(self, mock_input, mock_repository_class, mock_presenter_class, mock_use_case_class):
        """Test execution with specific product ID."""
        # Setup mocks
        self.mock_session_repository.is_user_logged_in.return_value = True
        self.mock_session_repository.get_order_account.return_value = "TEST_ACCOUNT"
        
        mock_repository = Mock()
        mock_presenter = Mock()
        mock_use_case = Mock()
        mock_use_case.execute.return_value = {"status": "success", "positions": ["position1"]}
        
        mock_repository_class.return_value = mock_repository
        mock_presenter_class.return_value = mock_presenter
        mock_use_case_class.return_value = mock_use_case
        
        controller = GetPositionController(self.mock_service_container)
        
        with patch('builtins.print') as mock_print:
            controller.execute()
        
        # Verify input DTO was created with specific product_id
        call_args = mock_use_case.execute.call_args[0][0]
        assert call_args.product_id == "MTX"
        assert call_args.order_account == "TEST_ACCOUNT"

    def test_service_container_dependency_injection(self):
        """Test that service container dependencies are properly injected."""
        controller = GetPositionController(self.mock_service_container)
        
        # Verify all dependencies are properly set
        assert controller.service_container is self.mock_service_container
        assert controller.logger is self.mock_service_container.logger
        assert controller.session_repository is self.mock_service_container.session_repository

    @patch('src.app.cli_pfcf.controllers.get_position_controller.GetPositionUseCase')
    @patch('src.app.cli_pfcf.controllers.get_position_controller.GetPositionPresenter')
    @patch('src.app.cli_pfcf.controllers.get_position_controller.PFCFPositionRepository')
    @patch('builtins.input', return_value='TX')
    def test_component_integration(self, mock_input, mock_repository_class, mock_presenter_class, mock_use_case_class):
        """Test integration between controller components."""
        # Setup mocks
        self.mock_session_repository.is_user_logged_in.return_value = True
        self.mock_session_repository.get_order_account.return_value = "ACCOUNT123"
        
        mock_repository = Mock()
        mock_presenter = Mock()
        mock_use_case = Mock()
        mock_use_case.execute.return_value = "formatted_output"
        
        mock_repository_class.return_value = mock_repository
        mock_presenter_class.return_value = mock_presenter
        mock_use_case_class.return_value = mock_use_case
        
        controller = GetPositionController(self.mock_service_container)
        
        with patch('builtins.print') as mock_print:
            controller.execute()
        
        # Verify the full flow
        # 1. Check login status
        self.mock_session_repository.is_user_logged_in.assert_called_once()
        
        # 2. Create infrastructure components
        mock_repository_class.assert_called_once_with(client=self.mock_exchange_client)
        mock_presenter_class.assert_called_once()
        mock_use_case_class.assert_called_once_with(mock_repository, mock_presenter, self.mock_logger)
        
        # 3. Get user input
        self.mock_session_repository.get_order_account.assert_called_once()
        mock_input.assert_called_once()
        
        # 4. Execute use case and display result
        mock_use_case.execute.assert_called_once()
        # Print is called twice: once for account display, once for result
        assert mock_print.call_count == 2
        mock_print.assert_any_call("Account: ACCOUNT123")
        mock_print.assert_any_call("formatted_output")

    @patch('builtins.input', side_effect=Exception("Input error"))
    def test_input_error_handling(self, mock_input):
        """Test error handling during input."""
        self.mock_session_repository.is_user_logged_in.return_value = True
        self.mock_session_repository.get_order_account.return_value = "TEST_ACCOUNT"
        
        controller = GetPositionController(self.mock_service_container)
        
        # Should raise the input exception
        with pytest.raises(Exception, match="Input error"):
            controller.execute()