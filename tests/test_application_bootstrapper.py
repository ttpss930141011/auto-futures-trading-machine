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
    BootstrapResult,
    ValidationResult,
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

    @patch("src.app.bootstrap.application_bootstrapper.PFCFApi")
    @patch("src.app.bootstrap.application_bootstrapper.LoggerDefault")
    @patch("src.app.bootstrap.application_bootstrapper.Config")
    def test_initialize_core_components(
        self,
        mock_config_class: Mock,
        mock_logger_class: Mock,
        mock_api_class: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """Test initialization of core components.

        Args:
            mock_config_class: Mocked Config class
            mock_logger_class: Mocked LoggerDefault class
            mock_api_class: Mocked PFCFApi class
            bootstrapper: ApplicationBootstrapper instance
        """
        # Setup mocks
        mock_api = Mock()
        mock_logger = Mock()
        mock_config = Mock()

        mock_api_class.return_value = mock_api
        mock_logger_class.return_value = mock_logger
        mock_config_class.return_value = mock_config

        bootstrapper._initialize_core_components()

        # Verify components were created
        assert bootstrapper._exchange_api == mock_api
        assert bootstrapper._logger == mock_logger
        assert bootstrapper._config == mock_config

        # Verify logger was used
        mock_logger.log_info.assert_called_with("Core components initialized successfully")

    def test_validate_configuration_success(self, bootstrapper: ApplicationBootstrapper) -> None:
        """Test successful configuration validation.

        Args:
            bootstrapper: ApplicationBootstrapper instance
        """
        # Setup mock config
        mock_config = Mock()
        mock_config.DLL_GATEWAY_BIND_ADDRESS = "tcp://127.0.0.1:5555"
        mock_config.DLL_GATEWAY_CONNECT_ADDRESS = "tcp://127.0.0.1:5555"
        mock_config.DLL_GATEWAY_REQUEST_TIMEOUT_MS = 5000
        mock_config.DEFAULT_CONDITION_FILE_PATH = "/path/to/conditions"
        mock_config.DEFAULT_SESSION_FILE_PATH = "/path/to/session"

        bootstrapper._config = mock_config

        result = bootstrapper.validate_configuration()

        assert result.is_valid is True
        assert len(result.error_messages) == 0

    def test_validate_configuration_missing_config(
        self, bootstrapper: ApplicationBootstrapper
    ) -> None:
        """Test configuration validation with missing config.

        Args:
            bootstrapper: ApplicationBootstrapper instance
        """
        bootstrapper._config = None

        result = bootstrapper.validate_configuration()

        assert result.is_valid is False
        assert "Configuration not initialized" in result.error_messages

    def test_validate_configuration_invalid_values(
        self, bootstrapper: ApplicationBootstrapper
    ) -> None:
        """Test configuration validation with invalid values.

        Args:
            bootstrapper: ApplicationBootstrapper instance
        """
        # Setup mock config with invalid values
        mock_config = Mock()
        mock_config.DLL_GATEWAY_BIND_ADDRESS = None
        mock_config.DLL_GATEWAY_CONNECT_ADDRESS = ""
        mock_config.DLL_GATEWAY_REQUEST_TIMEOUT_MS = -1

        # Missing required paths
        del mock_config.DEFAULT_CONDITION_FILE_PATH
        del mock_config.DEFAULT_SESSION_FILE_PATH

        bootstrapper._config = mock_config

        result = bootstrapper.validate_configuration()

        assert result.is_valid is False
        assert "DLL Gateway bind address not configured" in result.error_messages
        assert "DLL Gateway connect address not configured" in result.error_messages
        assert "Invalid DLL Gateway request timeout" in result.error_messages

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
    @patch.object(ApplicationBootstrapper, "validate_configuration")
    @patch.object(ApplicationBootstrapper, "_initialize_core_components")
    @patch.object(ApplicationBootstrapper, "_create_required_directories")
    def test_bootstrap_success(
        self,
        mock_create_dirs: Mock,
        mock_init_components: Mock,
        mock_validate: Mock,
        mock_create_container: Mock,
        mock_create_manager: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """Test successful bootstrap process.

        Args:
            mock_create_dirs: Mocked _create_required_directories method
            mock_init_components: Mocked _initialize_core_components method
            mock_validate: Mocked validate_configuration method
            mock_create_container: Mocked create_service_container method
            mock_create_manager: Mocked _create_system_manager method
            bootstrapper: ApplicationBootstrapper instance
        """
        # Setup mocks
        mock_validate.return_value = ValidationResult(is_valid=True, error_messages=[])
        mock_container = Mock()
        mock_create_container.return_value = mock_container
        mock_manager = Mock()
        mock_create_manager.return_value = mock_manager

        result = bootstrapper.bootstrap()

        # Verify all steps were called in order
        mock_create_dirs.assert_called_once()
        mock_init_components.assert_called_once()
        mock_validate.assert_called_once()
        mock_create_container.assert_called_once()
        mock_create_manager.assert_called_once_with(mock_container)

        # Verify result
        assert result.success is True
        assert result.system_manager == mock_manager
        assert result.service_container == mock_container
        assert result.error_message is None

    @patch.object(ApplicationBootstrapper, "validate_configuration")
    @patch.object(ApplicationBootstrapper, "_initialize_core_components")
    @patch.object(ApplicationBootstrapper, "_create_required_directories")
    def test_bootstrap_validation_failure(
        self,
        mock_create_dirs: Mock,
        mock_init_components: Mock,
        mock_validate: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """Test bootstrap with validation failure.

        Args:
            mock_create_dirs: Mocked _create_required_directories method
            mock_init_components: Mocked _initialize_core_components method
            mock_validate: Mocked validate_configuration method
            bootstrapper: ApplicationBootstrapper instance
        """
        # Setup validation failure
        mock_validate.return_value = ValidationResult(
            is_valid=False, error_messages=["Error 1", "Error 2"]
        )

        result = bootstrapper.bootstrap()

        # Verify result
        assert result.success is False
        assert result.system_manager is None
        assert result.service_container is None
        assert result.error_message == "Error 1; Error 2"

    @patch.object(ApplicationBootstrapper, "_create_required_directories")
    def test_bootstrap_exception_handling(
        self,
        mock_create_dirs: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """Test bootstrap exception handling.

        Args:
            mock_create_dirs: Mocked _create_required_directories method
            bootstrapper: ApplicationBootstrapper instance
        """
        # Setup exception
        mock_create_dirs.side_effect = Exception("Test error")

        result = bootstrapper.bootstrap()

        # Verify result
        assert result.success is False
        assert result.error_message == "Bootstrap failed: Test error"

    @patch("src.app.bootstrap.application_bootstrapper.DllGatewayServer")
    @patch("src.app.bootstrap.application_bootstrapper.SystemManager")
    @patch("src.app.bootstrap.application_bootstrapper.StatusChecker")
    @patch("src.app.bootstrap.application_bootstrapper.ProcessManagerService")
    @patch("src.app.bootstrap.application_bootstrapper.GatewayInitializerService")
    @patch("src.app.bootstrap.application_bootstrapper.PortCheckerService")
    def test_create_system_manager(
        self,
        mock_port_checker_class: Mock,
        mock_gateway_init_class: Mock,
        mock_process_manager_class: Mock,
        mock_status_checker_class: Mock,
        mock_system_manager_class: Mock,
        mock_gateway_server_class: Mock,
        bootstrapper: ApplicationBootstrapper,
    ) -> None:
        """Test system manager creation.

        Args:
            mock_port_checker_class: Mocked PortCheckerService class
            mock_gateway_init_class: Mocked GatewayInitializerService class
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
        mock_gateway_init = Mock()
        mock_process_manager = Mock()
        mock_status_checker = Mock()
        mock_system_manager = Mock()

        mock_gateway_server_class.return_value = mock_gateway_server
        mock_port_checker_class.return_value = mock_port_checker
        mock_gateway_init_class.return_value = mock_gateway_init
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
        mock_gateway_init_class.assert_called_once_with(mock_config, mock_logger, mock_exchange_api)
        mock_process_manager_class.assert_called_once_with(mock_config, mock_logger)
        mock_status_checker_class.assert_called_once_with(mock_service_container)

        # Verify system manager was created
        mock_system_manager_class.assert_called_once_with(
            logger=mock_logger,
            gateway_server=mock_gateway_server,
            port_checker=mock_port_checker,
            gateway_initializer=mock_gateway_init,
            process_manager=mock_process_manager,
            status_checker=mock_status_checker,
        )

        assert result == mock_system_manager
