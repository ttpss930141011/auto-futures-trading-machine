"""Tests for SystemManager class.

This module contains unit tests for the SystemManager class
to ensure proper infrastructure service management.
"""

from unittest.mock import Mock, patch, MagicMock
import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

from src.infrastructure.services.system_manager import (
    SystemManager,
    ComponentStatus,
    SystemStartupResult,
    SystemHealth,
)


class TestSystemManager:
    """Test cases for SystemManager class."""

    @pytest.fixture
    def mock_dependencies(self, mocker: "MockerFixture") -> dict:
        """Create mock dependencies for SystemManager.

        Args:
            mocker: Pytest mocker fixture

        Returns:
            Dictionary of mocked dependencies
        """
        return {
            "logger": mocker.Mock(),
            "gateway_server": mocker.Mock(),
            "port_checker": mocker.Mock(),
            "gateway_initializer": mocker.Mock(),
            "process_manager": mocker.Mock(),
            "status_checker": mocker.Mock(),
        }

    @pytest.fixture
    def system_manager(self, mock_dependencies: dict) -> SystemManager:
        """Create SystemManager instance with mocked dependencies.

        Args:
            mock_dependencies: Dictionary of mocked dependencies

        Returns:
            SystemManager instance
        """
        return SystemManager(**mock_dependencies)

    def test_init(self, mock_dependencies: dict) -> None:
        """Test SystemManager initialization.

        Args:
            mock_dependencies: Dictionary of mocked dependencies
        """
        manager = SystemManager(**mock_dependencies)

        assert manager._logger == mock_dependencies["logger"]
        assert manager._gateway_server == mock_dependencies["gateway_server"]
        assert manager._port_checker == mock_dependencies["port_checker"]
        assert manager._gateway_initializer == mock_dependencies["gateway_initializer"]
        assert manager._process_manager == mock_dependencies["process_manager"]
        assert manager._status_checker == mock_dependencies["status_checker"]

        # Check initial component status
        assert manager._component_status["gateway"] == ComponentStatus.STOPPED
        assert manager._component_status["strategy"] == ComponentStatus.STOPPED
        assert manager._component_status["order_executor"] == ComponentStatus.STOPPED
        assert manager._startup_time is None

    def test_start_trading_system_success(
        self, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test successful trading system startup.

        Args:
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        # Setup mocks
        mock_dependencies["port_checker"].check_port_availability.return_value = True
        mock_dependencies["gateway_server"].start.return_value = True

        with patch.object(system_manager, "_start_strategy", return_value=True), patch.object(
            system_manager, "_start_order_executor", return_value=True
        ), patch("time.sleep"), patch("time.time", return_value=1234567890):

            result = system_manager.start_trading_system()

        # Verify result
        assert result.success is True
        assert result.gateway_status == ComponentStatus.RUNNING
        assert result.strategy_status == ComponentStatus.RUNNING
        assert result.order_executor_status == ComponentStatus.RUNNING
        assert result.error_message is None

        # Verify startup time was set
        assert system_manager._startup_time == 1234567890

        # Verify logger was called with any log_info call
        assert mock_dependencies["logger"].log_info.called

    def test_start_trading_system_gateway_failure(
        self, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test trading system startup with gateway failure.

        Args:
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        # Setup mocks - gateway fails
        mock_dependencies["port_checker"].check_port_availability.return_value = False

        result = system_manager.start_trading_system()

        # Verify result
        assert result.success is False
        assert result.gateway_status == ComponentStatus.ERROR
        assert result.strategy_status == ComponentStatus.STOPPED
        assert result.order_executor_status == ComponentStatus.STOPPED
        assert result.error_message == "Failed to start Gateway"

    def test_start_trading_system_partial_failure(
        self, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test trading system startup with partial failure.

        Args:
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        # Setup mocks - gateway succeeds, strategy fails
        mock_dependencies["port_checker"].check_port_availability.return_value = True
        mock_dependencies["gateway_server"].start.return_value = True

        with patch.object(system_manager, "_start_strategy", return_value=False), patch.object(
            system_manager, "_start_order_executor", return_value=True
        ), patch("time.sleep"):

            result = system_manager.start_trading_system()

        # Verify result
        assert result.success is False
        assert result.gateway_status == ComponentStatus.RUNNING
        assert result.strategy_status == ComponentStatus.ERROR
        assert result.order_executor_status == ComponentStatus.RUNNING

    def test_stop_trading_system(
        self, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test stopping the trading system.

        Args:
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        # Set components as running
        system_manager._component_status = {
            "gateway": ComponentStatus.RUNNING,
            "strategy": ComponentStatus.RUNNING,
            "order_executor": ComponentStatus.RUNNING,
        }
        system_manager._startup_time = 1234567890

        system_manager.stop_trading_system()

        # Verify all components stopped
        assert system_manager._component_status["gateway"] == ComponentStatus.STOPPED
        assert system_manager._component_status["strategy"] == ComponentStatus.STOPPED
        assert system_manager._component_status["order_executor"] == ComponentStatus.STOPPED
        assert system_manager._startup_time is None

        # Verify cleanup methods called
        mock_dependencies["process_manager"].cleanup_processes.assert_called_once()
        mock_dependencies["gateway_server"].stop.assert_called_once()
        mock_dependencies["logger"].log_info.assert_called_with(
            "Trading system stopped successfully"
        )

    def test_get_system_health_all_running(self, system_manager: SystemManager) -> None:
        """Test getting system health when all components are running.

        Args:
            system_manager: SystemManager instance
        """
        # Set components as running
        system_manager._component_status = {
            "gateway": ComponentStatus.RUNNING,
            "strategy": ComponentStatus.RUNNING,
            "order_executor": ComponentStatus.RUNNING,
        }
        system_manager._startup_time = 1234567890

        with patch("time.time", return_value=1234567900):  # 10 seconds later
            health = system_manager.get_system_health()

        assert health.is_healthy is True
        assert health.components == system_manager._component_status
        assert health.uptime_seconds == 10.0
        assert health.last_check_timestamp == 1234567900

    def test_get_system_health_partial_running(self, system_manager: SystemManager) -> None:
        """Test getting system health when some components are not running.

        Args:
            system_manager: SystemManager instance
        """
        # Set mixed component status
        system_manager._component_status = {
            "gateway": ComponentStatus.RUNNING,
            "strategy": ComponentStatus.ERROR,
            "order_executor": ComponentStatus.STOPPED,
        }

        with patch("time.time", return_value=1234567890):
            health = system_manager.get_system_health()

        assert health.is_healthy is False
        assert health.components == system_manager._component_status
        assert health.uptime_seconds == 0.0  # No startup time set
        assert health.last_check_timestamp == 1234567890

    def test_restart_component_gateway(
        self, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test restarting the gateway component.

        Args:
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        # Setup initial state
        system_manager._component_status["gateway"] = ComponentStatus.RUNNING

        # Setup mocks
        mock_dependencies["port_checker"].check_port_availability.return_value = True
        mock_dependencies["gateway_server"].start.return_value = True

        result = system_manager.restart_component("gateway")

        assert result is True
        assert system_manager._component_status["gateway"] == ComponentStatus.RUNNING

        # Verify stop and start were called
        mock_dependencies["gateway_server"].stop.assert_called_once()
        mock_dependencies["gateway_server"].start.assert_called_once()

    def test_restart_component_unknown(
        self, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test restarting an unknown component.

        Args:
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        result = system_manager.restart_component("unknown")

        assert result is False
        mock_dependencies["logger"].log_error.assert_called_with("Unknown component: unknown")

    def test_restart_component_failure(
        self, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test restarting a component that fails to start.

        Args:
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        # Setup mocks - gateway fails to restart
        mock_dependencies["port_checker"].check_port_availability.return_value = False

        result = system_manager.restart_component("gateway")

        assert result is False
        assert system_manager._component_status["gateway"] == ComponentStatus.ERROR

    def test_start_gateway_port_unavailable(
        self, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test starting gateway when port is unavailable.

        Args:
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        mock_dependencies["port_checker"].check_port_availability.return_value = False

        result = system_manager._start_gateway()

        assert result is False
        mock_dependencies["logger"].log_error.assert_called_with("Gateway port is not available")

    def test_start_gateway_server_failure(
        self, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test starting gateway when server fails to start.

        Args:
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        mock_dependencies["port_checker"].check_port_availability.return_value = True
        mock_dependencies["gateway_server"].start.return_value = False

        result = system_manager._start_gateway()

        assert result is False
        mock_dependencies["logger"].log_error.assert_called_with("Failed to start Gateway server")

    @patch("src.interactor.use_cases.start_strategy_use_case.StartStrategyUseCase")
    def test_start_strategy_success(
        self, mock_use_case_class: Mock, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test starting strategy successfully.

        Args:
            mock_use_case_class: Mocked StartStrategyUseCase class
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        mock_use_case = Mock()
        mock_use_case.execute.return_value = True
        mock_use_case_class.return_value = mock_use_case

        result = system_manager._start_strategy()

        assert result is True
        mock_use_case_class.assert_called_once_with(
            logger=mock_dependencies["logger"],
            process_manager_service=mock_dependencies["process_manager"],
        )
        mock_use_case.execute.assert_called_once()

    @patch("src.interactor.use_cases.start_order_executor_use_case.StartOrderExecutorUseCase")
    def test_start_order_executor_success(
        self, mock_use_case_class: Mock, system_manager: SystemManager, mock_dependencies: dict
    ) -> None:
        """Test starting order executor successfully.

        Args:
            mock_use_case_class: Mocked StartOrderExecutorUseCase class
            system_manager: SystemManager instance
            mock_dependencies: Dictionary of mocked dependencies
        """
        mock_use_case = Mock()
        mock_use_case.execute.return_value = True
        mock_use_case_class.return_value = mock_use_case

        result = system_manager._start_order_executor()

        assert result is True
        mock_use_case_class.assert_called_once_with(
            logger=mock_dependencies["logger"],
            process_manager_service=mock_dependencies["process_manager"],
        )
        mock_use_case.execute.assert_called_once()
