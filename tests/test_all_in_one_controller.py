"""Tests for refactored AllInOneController class.

This module contains unit tests for the AllInOneController class
to ensure proper user interaction and delegation to SystemManager.
"""

from unittest.mock import Mock, patch
import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

from src.app.cli_pfcf.controllers.all_in_one_controller import AllInOneController
from src.infrastructure.services.system_manager import (
    ComponentStatus,
    SystemStartupResult,
)


class TestAllInOneController:
    """Test cases for refactored AllInOneController class."""

    @pytest.fixture
    def mock_service_container(self, mocker: "MockerFixture") -> Mock:
        """Create mock service container.

        Args:
            mocker: Pytest mocker fixture

        Returns:
            Mock service container
        """
        container = mocker.Mock()
        container.logger = mocker.Mock()
        container.session_repository = mocker.Mock()
        return container

    @pytest.fixture
    def mock_system_manager(self, mocker: "MockerFixture") -> Mock:
        """Create mock system manager.

        Args:
            mocker: Pytest mocker fixture

        Returns:
            Mock system manager
        """
        return mocker.Mock()

    @pytest.fixture
    def controller(
        self, mock_service_container: Mock, mock_system_manager: Mock
    ) -> AllInOneController:
        """Create AllInOneController instance with mocks.

        Args:
            mock_service_container: Mock service container
            mock_system_manager: Mock system manager

        Returns:
            AllInOneController instance
        """
        return AllInOneController(mock_service_container, mock_system_manager)

    def test_init(self, mock_service_container: Mock, mock_system_manager: Mock) -> None:
        """Test AllInOneController initialization.

        Args:
            mock_service_container: Mock service container
            mock_system_manager: Mock system manager
        """
        controller = AllInOneController(mock_service_container, mock_system_manager)

        assert controller._service_container == mock_service_container
        assert controller._system_manager == mock_system_manager
        assert controller._logger == mock_service_container.logger
        assert controller._session_repository == mock_service_container.session_repository
        assert controller._startup_status_use_case is not None

    def test_execute_user_not_logged_in(
        self, controller: AllInOneController, mock_service_container: Mock, capsys
    ) -> None:
        """Test execute when user is not logged in.

        Args:
            controller: AllInOneController instance
            mock_service_container: Mock service container
            capsys: Pytest capture fixture
        """
        # Setup mock
        mock_service_container.session_repository.is_user_logged_in.return_value = False

        controller.execute()

        # Verify behavior
        mock_service_container.logger.log_info.assert_called_with("User not logged in")

        # Check output
        captured = capsys.readouterr()
        assert "Please login first (option 1)" in captured.out

    def test_execute_prerequisites_not_met(
        self,
        controller: AllInOneController,
        mock_service_container: Mock,
        capsys,
    ) -> None:
        """Test execute when prerequisites are not met.

        Args:
            controller: AllInOneController instance
            mock_service_container: Mock service container
            capsys: Pytest capture fixture
        """
        # Setup mocks
        mock_service_container.session_repository.is_user_logged_in.return_value = True

        # Mock the use case
        mock_use_case = Mock()
        mock_use_case.execute.return_value = {
            "logged_in": True,
            "item_registered": False,
            "order_account_selected": True,
            "has_conditions": False,
        }
        controller._startup_status_use_case = mock_use_case

        controller.execute()

        # Verify behavior
        mock_service_container.logger.log_warning.assert_called_with(
            "Prerequisites not met. Please complete the setup before starting."
        )

        # Check output
        captured = capsys.readouterr()
        assert "System Prerequisites" in captured.out
        assert "Item registered: ✗" in captured.out
        assert "Trading conditions defined: ✗" in captured.out

    def test_execute_success(
        self,
        controller: AllInOneController,
        mock_service_container: Mock,
        mock_system_manager: Mock,
        capsys,
    ) -> None:
        """Test successful execution.

        Args:
            controller: AllInOneController instance
            mock_service_container: Mock service container
            mock_system_manager: Mock system manager
            capsys: Pytest capture fixture
        """
        # Setup mocks
        mock_service_container.session_repository.is_user_logged_in.return_value = True

        # Mock the use case
        mock_use_case = Mock()
        mock_use_case.execute.return_value = {
            "logged_in": True,
            "item_registered": True,
            "order_account_selected": True,
            "has_conditions": True,
        }
        controller._startup_status_use_case = mock_use_case

        startup_result = SystemStartupResult(
            success=True,
            gateway_status=ComponentStatus.RUNNING,
            strategy_status=ComponentStatus.RUNNING,
            order_executor_status=ComponentStatus.RUNNING,
        )
        mock_system_manager.start_trading_system.return_value = startup_result

        controller.execute()

        # Verify system manager was called
        mock_system_manager.start_trading_system.assert_called_once()

        # Check output
        captured = capsys.readouterr()
        assert "Starting All Trading System Components" in captured.out
        assert "Overall Status: ✓ Success" in captured.out
        assert "Gateway: ✓ Running" in captured.out
        assert "All system components have been started successfully" in captured.out

    def test_execute_partial_failure(
        self,
        controller: AllInOneController,
        mock_service_container: Mock,
        mock_system_manager: Mock,
        capsys,
    ) -> None:
        """Test execution with partial failure.

        Args:
            controller: AllInOneController instance
            mock_service_container: Mock service container
            mock_system_manager: Mock system manager
            capsys: Pytest capture fixture
        """
        # Setup mocks
        mock_service_container.session_repository.is_user_logged_in.return_value = True

        # Mock the use case
        mock_use_case = Mock()
        mock_use_case.execute.return_value = {
            "logged_in": True,
            "item_registered": True,
            "order_account_selected": True,
            "has_conditions": True,
        }
        controller._startup_status_use_case = mock_use_case

        startup_result = SystemStartupResult(
            success=False,
            gateway_status=ComponentStatus.RUNNING,
            strategy_status=ComponentStatus.ERROR,
            order_executor_status=ComponentStatus.STOPPED,
            error_message="Strategy failed to start",
        )
        mock_system_manager.start_trading_system.return_value = startup_result

        controller.execute()

        # Check output
        captured = capsys.readouterr()
        assert "Overall Status: ✗ Failed" in captured.out
        assert "Strategy: ✗ Error" in captured.out
        assert "Failed to start all system components" in captured.out
        assert "Error: Strategy failed to start" in captured.out

    def test_execute_exception_handling(
        self,
        controller: AllInOneController,
        mock_service_container: Mock,
        mock_system_manager: Mock,
        capsys,
    ) -> None:
        """Test exception handling during execution.

        Args:
            controller: AllInOneController instance
            mock_service_container: Mock service container
            mock_system_manager: Mock system manager
            capsys: Pytest capture fixture
        """
        # Setup mocks
        mock_service_container.session_repository.is_user_logged_in.return_value = True

        # Mock the use case
        mock_use_case = Mock()
        mock_use_case.execute.return_value = {
            "logged_in": True,
            "item_registered": True,
            "order_account_selected": True,
            "has_conditions": True,
        }
        controller._startup_status_use_case = mock_use_case

        # Simulate exception
        mock_system_manager.start_trading_system.side_effect = Exception("Test error")

        controller.execute()

        # Verify error logging
        mock_service_container.logger.log_error.assert_called_with(
            "All-in-one controller error: Test error"
        )

        # Check output
        captured = capsys.readouterr()
        assert "ERROR: Failed to start system components: Test error" in captured.out

    def test_format_component_status(self, controller: AllInOneController) -> None:
        """Test component status formatting.

        Args:
            controller: AllInOneController instance
        """
        assert controller._format_component_status(ComponentStatus.RUNNING) == "✓ Running"
        assert controller._format_component_status(ComponentStatus.STOPPED) == "✗ Stopped"
        assert controller._format_component_status(ComponentStatus.ERROR) == "✗ Error"
        assert controller._format_component_status(ComponentStatus.STARTING) == "⟳ Starting"
        assert controller._format_component_status(ComponentStatus.STOPPING) == "⟳ Stopping"

    def test_display_status_summary(self, controller: AllInOneController, capsys) -> None:
        """Test status summary display.

        Args:
            controller: AllInOneController instance
            capsys: Pytest capture fixture
        """
        status_summary = {
            "logged_in": True,
            "item_registered": False,
            "order_account_selected": True,
            "has_conditions": False,
        }

        controller._display_status_summary(status_summary)

        captured = capsys.readouterr()
        assert "System Prerequisites" in captured.out
        assert "User logged in: ✓" in captured.out
        assert "Item registered: ✗" in captured.out
        assert "Order account selected: ✓" in captured.out
        assert "Trading conditions defined: ✗" in captured.out

    def test_display_success_message(self, controller: AllInOneController, capsys) -> None:
        """Test success message display.

        Args:
            controller: AllInOneController instance
            capsys: Pytest capture fixture
        """
        controller._display_success_message()

        captured = capsys.readouterr()
        assert "All system components have been started successfully" in captured.out
        assert "You can continue using the main menu" in captured.out
        assert "The system will automatically clean up" in captured.out

    def test_display_error_message_with_message(
        self, controller: AllInOneController, capsys
    ) -> None:
        """Test error message display with specific error.

        Args:
            controller: AllInOneController instance
            capsys: Pytest capture fixture
        """
        controller._display_error_message("Gateway port already in use")

        captured = capsys.readouterr()
        assert "Failed to start all system components" in captured.out
        assert "Error: Gateway port already in use" in captured.out
        assert "Please check the logs for more details" in captured.out

    def test_display_error_message_without_message(
        self, controller: AllInOneController, capsys
    ) -> None:
        """Test error message display without specific error.

        Args:
            controller: AllInOneController instance
            capsys: Pytest capture fixture
        """
        controller._display_error_message(None)

        captured = capsys.readouterr()
        assert "Failed to start all system components" in captured.out
        assert "Error:" not in captured.out
        assert "Please check the logs for more details" in captured.out
