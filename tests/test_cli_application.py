"""Tests for CLIApplication class.

This module contains unit tests for the CLIApplication class
to ensure proper CLI interaction and controller management.
"""

from unittest.mock import Mock, patch, call
import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

from src.app.cli_application import CLIApplication


class TestCLIApplication:
    """Test cases for CLIApplication class."""

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
    def mock_service_container(self, mocker: "MockerFixture") -> Mock:
        """Create mock service container.

        Args:
            mocker: Pytest mocker fixture

        Returns:
            Mock service container
        """
        container = mocker.Mock()
        container.config = mocker.Mock()
        container.config.DLL_GATEWAY_CONNECT_ADDRESS = "tcp://127.0.0.1:5555"
        return container

    @pytest.fixture
    def cli_app(self, mock_system_manager: Mock, mock_service_container: Mock) -> CLIApplication:
        """Create CLIApplication instance with mocks.

        Args:
            mock_system_manager: Mock system manager
            mock_service_container: Mock service container

        Returns:
            CLIApplication instance
        """
        return CLIApplication(mock_system_manager, mock_service_container)

    @patch("atexit.register")
    def test_init(
        self,
        mock_atexit: Mock,
        mock_system_manager: Mock,
        mock_service_container: Mock,
    ) -> None:
        """Test CLIApplication initialization.

        Args:
            mock_atexit: Mocked atexit.register
            mock_system_manager: Mock system manager
            mock_service_container: Mock service container
        """
        app = CLIApplication(mock_system_manager, mock_service_container)

        assert app._system_manager == mock_system_manager
        assert app._service_container == mock_service_container
        assert app._process_handler is None

        # Verify cleanup was registered
        mock_atexit.assert_called_once()

    @patch.object(CLIApplication, "_cleanup")
    @patch.object(CLIApplication, "_create_process_handler")
    @patch.object(CLIApplication, "_display_startup_info")
    def test_run_success(
        self,
        mock_display_info: Mock,
        mock_create_handler: Mock,
        mock_cleanup: Mock,
        cli_app: CLIApplication,
    ) -> None:
        """Test successful run of CLI application.

        Args:
            mock_display_info: Mocked _display_startup_info method
            mock_create_handler: Mocked _create_process_handler method
            mock_cleanup: Mocked _cleanup method
            cli_app: CLIApplication instance
        """
        # Setup mock process handler
        mock_handler = Mock()
        mock_create_handler.return_value = mock_handler

        cli_app.run()

        # Verify execution order
        mock_display_info.assert_called_once()
        mock_create_handler.assert_called_once()
        mock_handler.execute.assert_called_once()
        mock_cleanup.assert_called_once()

    @patch.object(CLIApplication, "_cleanup")
    @patch.object(CLIApplication, "_create_process_handler")
    @patch.object(CLIApplication, "_display_startup_info")
    def test_run_keyboard_interrupt(
        self,
        mock_display_info: Mock,
        mock_create_handler: Mock,
        mock_cleanup: Mock,
        cli_app: CLIApplication,
        capsys,
    ) -> None:
        """Test run with keyboard interrupt.

        Args:
            mock_display_info: Mocked _display_startup_info method
            mock_create_handler: Mocked _create_process_handler method
            mock_cleanup: Mocked _cleanup method
            cli_app: CLIApplication instance
            capsys: Pytest capture fixture
        """
        # Setup mock to raise KeyboardInterrupt
        mock_handler = Mock()
        mock_handler.execute.side_effect = KeyboardInterrupt()
        mock_create_handler.return_value = mock_handler

        cli_app.run()

        # Verify cleanup was called
        mock_cleanup.assert_called_once()

        # Check output
        captured = capsys.readouterr()
        assert "Program terminated by user" in captured.out

    @patch.object(CLIApplication, "_cleanup")
    @patch.object(CLIApplication, "_display_startup_info")
    def test_run_exception(
        self,
        mock_display_info: Mock,
        mock_cleanup: Mock,
        cli_app: CLIApplication,
        capsys,
    ) -> None:
        """Test run with exception.

        Args:
            mock_display_info: Mocked _display_startup_info method
            mock_cleanup: Mocked _cleanup method
            cli_app: CLIApplication instance
            capsys: Pytest capture fixture
        """
        # Setup mock to raise exception
        mock_display_info.side_effect = Exception("Test error")

        cli_app.run()

        # Verify cleanup was called
        mock_cleanup.assert_called_once()

        # Check output
        captured = capsys.readouterr()
        assert "ERROR: Test error" in captured.out

    @patch("src.app.cli_application.AllInOneController")
    @patch("src.app.cli_application.GetPositionController")
    @patch("src.app.cli_application.ShowFuturesController")
    @patch("src.app.cli_application.SendMarketOrderController")
    @patch("src.app.cli_application.SelectOrderAccountController")
    @patch("src.app.cli_application.CreateConditionController")
    @patch("src.app.cli_application.RegisterItemController")
    @patch("src.app.cli_application.UserLogoutController")
    @patch("src.app.cli_application.UserLoginController")
    @patch("src.app.cli_application.ExitController")
    @patch("src.app.cli_application.CliMemoryProcessHandler")
    def test_create_process_handler(
        self,
        mock_handler_class: Mock,
        mock_exit_ctrl: Mock,
        mock_login_ctrl: Mock,
        mock_logout_ctrl: Mock,
        mock_register_ctrl: Mock,
        mock_condition_ctrl: Mock,
        mock_account_ctrl: Mock,
        mock_order_ctrl: Mock,
        mock_futures_ctrl: Mock,
        mock_position_ctrl: Mock,
        mock_all_in_one_ctrl: Mock,
        cli_app: CLIApplication,
        mock_service_container: Mock,
        mock_system_manager: Mock,
    ) -> None:
        """Test process handler creation.

        Args:
            mock_handler_class: Mocked CliMemoryProcessHandler class
            mock_exit_ctrl: Mocked ExitController class
            mock_login_ctrl: Mocked UserLoginController class
            mock_logout_ctrl: Mocked UserLogoutController class
            mock_register_ctrl: Mocked RegisterItemController class
            mock_condition_ctrl: Mocked CreateConditionController class
            mock_account_ctrl: Mocked SelectOrderAccountController class
            mock_order_ctrl: Mocked SendMarketOrderController class
            mock_futures_ctrl: Mocked ShowFuturesController class
            mock_position_ctrl: Mocked GetPositionController class
            mock_all_in_one_ctrl: Mocked AllInOneController class
            cli_app: CLIApplication instance
            mock_service_container: Mock service container
            mock_system_manager: Mock system manager
        """
        # Setup mock handler
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler

        # Create mock controllers
        controllers = {
            "exit": Mock(),
            "login": Mock(),
            "logout": Mock(),
            "register": Mock(),
            "condition": Mock(),
            "account": Mock(),
            "order": Mock(),
            "futures": Mock(),
            "position": Mock(),
            "all_in_one": Mock(),
        }

        mock_exit_ctrl.return_value = controllers["exit"]
        mock_login_ctrl.return_value = controllers["login"]
        mock_logout_ctrl.return_value = controllers["logout"]
        mock_register_ctrl.return_value = controllers["register"]
        mock_condition_ctrl.return_value = controllers["condition"]
        mock_account_ctrl.return_value = controllers["account"]
        mock_order_ctrl.return_value = controllers["order"]
        mock_futures_ctrl.return_value = controllers["futures"]
        mock_position_ctrl.return_value = controllers["position"]
        mock_all_in_one_ctrl.return_value = controllers["all_in_one"]

        result = cli_app._create_process_handler()

        # Verify handler was created
        mock_handler_class.assert_called_once_with(mock_service_container)
        assert result == mock_handler

        # Verify all options were added
        expected_calls = [
            call("0", controllers["exit"]),
            call("1", controllers["login"]),
            call("2", controllers["logout"], "protected"),
            call("3", controllers["register"], "protected"),
            call("4", controllers["condition"], "protected"),
            call("5", controllers["account"], "protected"),
            call("6", controllers["order"], "protected"),
            call("7", controllers["futures"], "protected"),
            call("8", controllers["position"], "protected"),
            call("10", controllers["all_in_one"], "protected"),
        ]

        mock_handler.add_option.assert_has_calls(expected_calls)

        # Verify AllInOneController was created with correct params
        mock_all_in_one_ctrl.assert_called_once_with(mock_service_container, mock_system_manager)

    def test_display_startup_info(
        self, cli_app: CLIApplication, mock_service_container: Mock, capsys
    ) -> None:
        """Test startup information display.

        Args:
            cli_app: CLIApplication instance
            mock_service_container: Mock service container
            capsys: Pytest capture fixture
        """
        cli_app._display_startup_info()

        captured = capsys.readouterr()
        assert "Initializing Auto Futures Trading Machine with DLL Gateway" in captured.out
        assert "DLL Gateway Server: Running on tcp://127.0.0.1:5555" in captured.out
        assert "Exchange API: Centralized access through gateway" in captured.out
        assert "Multi-process support: Enhanced security and stability" in captured.out
        assert "AllInOneController (option 10) now uses Gateway architecture" in captured.out

    def test_cleanup_success(
        self, cli_app: CLIApplication, mock_system_manager: Mock, capsys
    ) -> None:
        """Test successful cleanup.

        Args:
            cli_app: CLIApplication instance
            mock_system_manager: Mock system manager
            capsys: Pytest capture fixture
        """
        cli_app._cleanup()

        # Verify system manager was stopped
        mock_system_manager.stop_trading_system.assert_called_once()

        # Check output
        captured = capsys.readouterr()
        assert "Shutting down application..." in captured.out

    def test_cleanup_exception(
        self, cli_app: CLIApplication, mock_system_manager: Mock, capsys
    ) -> None:
        """Test cleanup with exception.

        Args:
            cli_app: CLIApplication instance
            mock_system_manager: Mock system manager
            capsys: Pytest capture fixture
        """
        # Setup mock to raise exception
        mock_system_manager.stop_trading_system.side_effect = Exception("Cleanup error")

        cli_app._cleanup()

        # Check output
        captured = capsys.readouterr()
        assert "Error during cleanup: Cleanup error" in captured.out
