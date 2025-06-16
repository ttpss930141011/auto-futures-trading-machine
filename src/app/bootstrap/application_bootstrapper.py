"""Application bootstrapper for dependency injection and initialization.

This module provides the ApplicationBootstrapper class which handles
the initialization sequence and dependency injection for the application.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.app.cli_pfcf.config import Config
from src.infrastructure.loggers.logger_default import LoggerDefault
from src.infrastructure.pfcf_client.api import PFCFApi
from src.infrastructure.repositories.condition_json_file_repository import (
    ConditionJsonFileRepository,
)
from src.infrastructure.repositories.session_json_file_repository import SessionJsonFileRepository
from src.infrastructure.services.dll_gateway_server import DllGatewayServer
from src.infrastructure.services.gateway.market_data_gateway_service import (
    MarketDataGatewayService,
)
from src.infrastructure.services.gateway.port_checker_service import PortCheckerService
from src.infrastructure.services.process.process_manager_service import ProcessManagerService
from src.infrastructure.services.service_container import ServiceContainer
from src.infrastructure.services.status_checker import StatusChecker
from src.infrastructure.services.system_manager import SystemManager


@dataclass
class BootstrapResult:
    """Result of the bootstrap operation."""

    success: bool
    system_manager: Optional[SystemManager] = None
    service_container: Optional[ServiceContainer] = None
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of configuration validation."""

    is_valid: bool
    error_messages: list[str]


class ApplicationBootstrapper:
    """Handles dependency injection and initialization sequence.

    This class follows the Single Responsibility Principle by focusing
    solely on application initialization and dependency setup.
    """

    def __init__(self) -> None:
        """Initialize the ApplicationBootstrapper."""
        self._logger: Optional[LoggerDefault] = None
        self._config: Optional[Config] = None
        self._exchange_api: Optional[PFCFApi] = None

    def bootstrap(self) -> BootstrapResult:
        """Bootstrap the application with all dependencies.

        Returns:
            BootstrapResult with system manager and service container
        """
        try:
            # Step 1: Create directories
            self._create_required_directories()

            # Step 2: Initialize core components
            self._initialize_core_components()

            # Step 3: Validate configuration
            validation_result = self.validate_configuration()
            if not validation_result.is_valid:
                return BootstrapResult(
                    success=False,
                    error_message="; ".join(validation_result.error_messages),
                )

            # Step 4: Create service container
            service_container = self.create_service_container()

            # Step 5: Create system manager
            system_manager = self._create_system_manager(service_container)

            return BootstrapResult(
                success=True,
                system_manager=system_manager,
                service_container=service_container,
            )

        except (RuntimeError, OSError, ValueError, Exception) as e:
            error_msg = f"Bootstrap failed: {str(e)}"
            if self._logger:
                self._logger.log_error(error_msg)
            return BootstrapResult(
                success=False,
                error_message=error_msg,
            )

    def create_service_container(self) -> ServiceContainer:
        """Create and configure the service container.

        Returns:
            Configured ServiceContainer instance
        """
        if not all([self._logger, self._config]):
            raise RuntimeError("Core components not initialized")

        # Create repositories
        session_repository = SessionJsonFileRepository(self._config.DEFAULT_SESSION_TIMEOUT)
        condition_repository = ConditionJsonFileRepository()

        # Create service container
        service_container = ServiceContainer(
            logger=self._logger,
            config=self._config,
            session_repository=session_repository,
            condition_repository=condition_repository,
            exchange_api=self._exchange_api,
        )

        return service_container

    def validate_configuration(self) -> ValidationResult:
        """Validate the application configuration.

        Returns:
            ValidationResult with validation status
        """
        errors = []

        if not self._config:
            errors.append("Configuration not initialized")
            return ValidationResult(is_valid=False, error_messages=errors)

        # Validate DLL Gateway configuration
        if not self._config.DLL_GATEWAY_BIND_ADDRESS:
            errors.append("DLL Gateway bind address not configured")

        if not self._config.DLL_GATEWAY_CONNECT_ADDRESS:
            errors.append("DLL Gateway connect address not configured")

        if self._config.DLL_GATEWAY_REQUEST_TIMEOUT_MS <= 0:
            errors.append("Invalid DLL Gateway request timeout")

        return ValidationResult(
            is_valid=len(errors) == 0,
            error_messages=errors,
        )

    def _create_required_directories(self) -> None:
        """Create required directories for the application."""
        # Create PID directory
        pid_dir = Path(__file__).resolve().parent.parent.parent.parent / "tmp" / "pids"
        pid_dir.mkdir(parents=True, exist_ok=True)

        # Create logs directory
        logs_dir = Path(__file__).resolve().parent.parent.parent.parent / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Create data directory for repositories
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_core_components(self) -> None:
        """Initialize core components needed for bootstrap."""
        # Initialize exchange API
        self._exchange_api = PFCFApi()

        # Initialize logger
        self._logger = LoggerDefault()

        # Initialize configuration
        self._config = Config()

        self._logger.log_info("Core components initialized successfully")

    def _create_system_manager(self, service_container: ServiceContainer) -> SystemManager:
        """Create the system manager with all dependencies.

        Args:
            service_container: The service container with dependencies

        Returns:
            Configured SystemManager instance
        """
        # Create DLL Gateway Server
        gateway_server = DllGatewayServer(
            exchange_client=self._exchange_api,
            config=self._config,
            logger=self._logger,
            bind_address=self._config.DLL_GATEWAY_BIND_ADDRESS,
            request_timeout_ms=self._config.DLL_GATEWAY_REQUEST_TIMEOUT_MS,
        )

        # Create infrastructure services
        port_checker = PortCheckerService(self._config, self._logger)
        market_data_gateway = MarketDataGatewayService(self._config, self._logger, self._exchange_api)
        process_manager = ProcessManagerService(self._config, self._logger)
        status_checker = StatusChecker(service_container)

        # Create and return system manager
        system_manager = SystemManager(
            logger=self._logger,
            gateway_server=gateway_server,
            port_checker=port_checker,
            market_data_gateway=market_data_gateway,
            process_manager=process_manager,
            status_checker=status_checker,
        )

        return system_manager
