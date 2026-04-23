"""Tests for ApplicationBootstrapper class.

This module contains unit tests for the ApplicationBootstrapper class
to ensure proper application initialization and dependency injection.
"""

from unittest.mock import Mock, patch, MagicMock
import pytest
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

from src.app.bootstrap.application_bootstrapper import (
    ApplicationBootstrapper,
    BootstrappedApp,
)


class TestApplicationBootstrapper:
    """Test cases for ApplicationBootstrapper class."""

    @pytest.fixture
    def bootstrapper(self) -> ApplicationBootstrapper:
        """Create ApplicationBootstrapper instance.

        Returns:
            ApplicationBootstrapper instance
        """
        return ApplicationBootstrapper()

    @patch("src.app.bootstrap.application_bootstrapper.Path.mkdir")
    def test_create_required_directories(
        self, mock_mkdir: Mock, bootstrapper: ApplicationBootstrapper
    ) -> None:
        """Test creation of required directories.

        Args:
            mock_mkdir: Mocked Path.mkdir method
            bootstrapper: ApplicationBootstrapper instance
        """
        bootstrapper._create_required_directories()

        # Verify mkdir was called for each required directory
        assert mock_mkdir.call_count >= 3  # pid_dir, logs_dir, data_dir

    @patch("src.app.bootstrap.application_bootstrapper.SimulatorExchangeAdapter")
    @patch("src.app.bootstrap.application_bootstrapper.PfcfExchangeAdapter")
    @patch("src.app.bootstrap.application_bootstrapper.LoggerDefault")
    @patch("src.app.bootstrap.application_bootstrapper.Config")
    def test_initialize_core_components_pfcf_mode(
        self,
        mock_config_class: Mock,
        mock_logger_class: Mock,
        mock_pfcf_class: Mock,
        mock_sim_class: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """EXCHANGE_MODE=pfcf selects PfcfExchangeAdapter."""
        mock_adapter = Mock()
        mock_logger = Mock()
        mock_config = Mock()
        mock_config.EXCHANGE_MODE = "pfcf"

        mock_pfcf_class.return_value = mock_adapter
        mock_logger_class.return_value = mock_logger
        mock_config_class.return_value = mock_config

        bootstrapper._initialize_core_components()

        assert bootstrapper._exchange_api == mock_adapter
        assert bootstrapper._logger == mock_logger
        assert bootstrapper._config == mock_config
        mock_pfcf_class.assert_called_once_with()
        mock_sim_class.assert_not_called()

    @patch("src.app.bootstrap.application_bootstrapper.SimulatorExchangeAdapter")
    @patch("src.app.bootstrap.application_bootstrapper.PfcfExchangeAdapter")
    @patch("src.app.bootstrap.application_bootstrapper.LoggerDefault")
    @patch("src.app.bootstrap.application_bootstrapper.Config")
    def test_initialize_core_components_simulator_mode(
        self,
        mock_config_class: Mock,
        mock_logger_class: Mock,
        mock_pfcf_class: Mock,
        mock_sim_class: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """EXCHANGE_MODE=simulator selects SimulatorExchangeAdapter."""
        mock_adapter = Mock()
        mock_config = Mock()
        mock_config.EXCHANGE_MODE = "simulator"

        mock_sim_class.return_value = mock_adapter
        mock_logger_class.return_value = Mock()
        mock_config_class.return_value = mock_config

        bootstrapper._initialize_core_components()

        assert bootstrapper._exchange_api == mock_adapter
        mock_sim_class.assert_called_once_with()
        mock_pfcf_class.assert_not_called()

    @patch("src.app.bootstrap.application_bootstrapper.SessionJsonFileRepository")
    @patch("src.app.bootstrap.application_bootstrapper.ConditionJsonFileRepository")
    @patch("src.app.bootstrap.application_bootstrapper.ServiceContainer")
    def test_create_service_container(
        self,
        mock_container_class: Mock,
        mock_condition_repo_class: Mock,
        mock_session_repo_class: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """Test service container creation.

        Args:
            mock_container_class: Mocked ServiceContainer class
            mock_condition_repo_class: Mocked ConditionJsonFileRepository class
            mock_session_repo_class: Mocked SessionJsonFileRepository class
            bootstrapper: ApplicationBootstrapper instance
        """
        # Setup mocks
        mock_logger = Mock()
        mock_config = Mock()
        mock_exchange_api = Mock()
        mock_config.DEFAULT_SESSION_TIMEOUT = 3600

        bootstrapper._logger = mock_logger
        bootstrapper._config = mock_config
        bootstrapper._exchange_api = mock_exchange_api

        mock_session_repo = Mock()
        mock_condition_repo = Mock()
        mock_container = Mock()

        mock_session_repo_class.return_value = mock_session_repo
        mock_condition_repo_class.return_value = mock_condition_repo
        mock_container_class.return_value = mock_container

        result = bootstrapper.create_service_container()

        # Verify repositories were created
        mock_session_repo_class.assert_called_once_with(3600)
        mock_condition_repo_class.assert_called_once()

        # Verify container was created with correct dependencies
        mock_container_class.assert_called_once_with(
            logger=mock_logger,
            config=mock_config,
            session_repository=mock_session_repo,
            condition_repository=mock_condition_repo,
            exchange_api=mock_exchange_api,
        )

        assert result == mock_container

    def test_create_service_container_missing_components(
        self, bootstrapper: ApplicationBootstrapper
    ) -> None:
        """Test service container creation with missing components.

        Args:
            bootstrapper: ApplicationBootstrapper instance
        """
        # Missing logger and config
        bootstrapper._logger = None
        bootstrapper._config = None

        with pytest.raises(RuntimeError, match="Core components not initialized"):
            bootstrapper.create_service_container()

    @patch.object(ApplicationBootstrapper, "_create_system_manager")
    @patch.object(ApplicationBootstrapper, "create_service_container")
    @patch.object(ApplicationBootstrapper, "_initialize_core_components")
    @patch.object(ApplicationBootstrapper, "_create_required_directories")
    def test_bootstrap_success(
        self,
        mock_create_dirs: Mock,
        mock_init_components: Mock,
        mock_create_container: Mock,
        mock_create_manager: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """bootstrap() returns a BootstrappedApp on success."""
        mock_container = Mock()
        mock_create_container.return_value = mock_container
        mock_manager = Mock()
        mock_create_manager.return_value = mock_manager

        result = bootstrapper.bootstrap()

        mock_create_dirs.assert_called_once()
        mock_init_components.assert_called_once()
        mock_create_container.assert_called_once()
        mock_create_manager.assert_called_once_with(mock_container)

        assert isinstance(result, BootstrappedApp)
        assert result.system_manager is mock_manager
        assert result.service_container is mock_container

    @patch.object(ApplicationBootstrapper, "_initialize_core_components")
    @patch.object(ApplicationBootstrapper, "_create_required_directories")
    def test_bootstrap_propagates_config_error(
        self,
        mock_create_dirs: Mock,
        mock_init_components: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """Config errors propagate to the caller instead of being swallowed."""
        mock_init_components.side_effect = ValueError(
            "DEALER_TEST_URL environment variable is required"
        )

        with pytest.raises(ValueError, match="DEALER_TEST_URL"):
            bootstrapper.bootstrap()

    @patch.object(ApplicationBootstrapper, "_create_required_directories")
    def test_bootstrap_propagates_unexpected_error(
        self,
        mock_create_dirs: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """Unexpected errors (e.g. mkdir failure) propagate to the caller."""
        mock_create_dirs.side_effect = OSError("permission denied")

        with pytest.raises(OSError, match="permission denied"):
            bootstrapper.bootstrap()

    @patch("src.app.bootstrap.application_bootstrapper.DllGatewayServer")
    @patch("src.app.bootstrap.application_bootstrapper.SystemManager")
    @patch("src.app.bootstrap.application_bootstrapper.StatusChecker")
    @patch("src.app.bootstrap.application_bootstrapper.ProcessManagerService")
    @patch("src.app.bootstrap.application_bootstrapper.MarketDataGatewayService")
    @patch("src.app.bootstrap.application_bootstrapper.PortCheckerService")
    def test_create_system_manager(
        self,
        mock_port_checker_class: Mock,
        mock_market_data_gateway_class: Mock,
        mock_process_manager_class: Mock,
        mock_status_checker_class: Mock,
        mock_system_manager_class: Mock,
        mock_gateway_server_class: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """Test system manager creation.

        Args:
            mock_port_checker_class: Mocked PortCheckerService class
            mock_market_data_gateway_class: Mocked MarketDataGatewayService class
            mock_process_manager_class: Mocked ProcessManagerService class
            mock_status_checker_class: Mocked StatusChecker class
            mock_system_manager_class: Mocked SystemManager class
            mock_gateway_server_class: Mocked DllGatewayServer class
            bootstrapper: ApplicationBootstrapper instance
        """
        # Setup mocks
        mock_logger = Mock()
        mock_config = Mock()
        mock_config.DLL_GATEWAY_BIND_ADDRESS = "tcp://127.0.0.1:5555"
        mock_config.DLL_GATEWAY_REQUEST_TIMEOUT_MS = 5000
        mock_exchange_api = Mock()
        mock_service_container = Mock()

        bootstrapper._logger = mock_logger
        bootstrapper._config = mock_config
        bootstrapper._exchange_api = mock_exchange_api

        # Create mock instances
        mock_gateway_server = Mock()
        mock_port_checker = Mock()
        mock_market_data_gateway = Mock()
        mock_process_manager = Mock()
        mock_status_checker = Mock()
        mock_system_manager = Mock()

        mock_gateway_server_class.return_value = mock_gateway_server
        mock_port_checker_class.return_value = mock_port_checker
        mock_market_data_gateway_class.return_value = mock_market_data_gateway
        mock_process_manager_class.return_value = mock_process_manager
        mock_status_checker_class.return_value = mock_status_checker
        mock_system_manager_class.return_value = mock_system_manager

        result = bootstrapper._create_system_manager(mock_service_container)

        # Verify gateway server was created
        mock_gateway_server_class.assert_called_once_with(
            exchange_client=mock_exchange_api,
            config=mock_config,
            logger=mock_logger,
            bind_address="tcp://127.0.0.1:5555",
            request_timeout_ms=5000,
        )

        # Verify services were created
        mock_port_checker_class.assert_called_once_with(mock_config, mock_logger)
        mock_market_data_gateway_class.assert_called_once_with(mock_config, mock_logger, mock_exchange_api)
        mock_process_manager_class.assert_called_once_with(mock_config, mock_logger)
        mock_status_checker_class.assert_called_once_with(mock_service_container)

        # Verify system manager was created
        mock_system_manager_class.assert_called_once_with(
            logger=mock_logger,
            gateway_server=mock_gateway_server,
            port_checker=mock_port_checker,
            market_data_gateway=mock_market_data_gateway,
            process_manager=mock_process_manager,
            status_checker=mock_status_checker,
        )

        assert result == mock_system_manager
