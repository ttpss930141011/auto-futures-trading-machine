"""System Manager for centralized infrastructure service management.

This module provides the SystemManager class which handles the lifecycle
of all infrastructure services in the trading system.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from src.infrastructure.loggers.logger_default import LoggerDefault
from src.infrastructure.services.dll_gateway_server import DllGatewayServer
from src.infrastructure.services.gateway.gateway_initializer_service import (
    GatewayInitializerService,
)
from src.infrastructure.services.gateway.port_checker_service import PortCheckerService
from src.infrastructure.services.process.process_manager_service import ProcessManagerService
from src.infrastructure.services.status_checker import StatusChecker
from src.interactor.use_cases.start_order_executor_use_case import (
    StartOrderExecutorUseCase,
)
from src.interactor.use_cases.start_strategy_use_case import StartStrategyUseCase


class ComponentStatus(Enum):
    """Status of a system component."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class SystemStartupResult:
    """Result of system startup operation."""

    success: bool
    gateway_status: ComponentStatus
    strategy_status: ComponentStatus
    order_executor_status: ComponentStatus
    error_message: Optional[str] = None


@dataclass
class SystemHealth:
    """Health status of the entire system."""

    is_healthy: bool
    components: Dict[str, ComponentStatus]
    uptime_seconds: float
    last_check_timestamp: float


class SystemManager:
    """Centralized infrastructure service management.

    This class follows the Single Responsibility Principle by focusing solely
    on managing the lifecycle of infrastructure services.
    """

    def __init__(
        self,
        logger: LoggerDefault,
        gateway_server: DllGatewayServer,
        port_checker: PortCheckerService,
        gateway_initializer: GatewayInitializerService,
        process_manager: ProcessManagerService,
        status_checker: StatusChecker,
    ) -> None:
        """Initialize the SystemManager.

        Args:
            logger: Logger for recording events
            gateway_server: DLL Gateway server instance
            port_checker: Service for checking port availability
            gateway_initializer: Service for initializing gateway
            process_manager: Service for managing processes
            status_checker: Service for checking system status
        """
        self._logger = logger
        self._gateway_server = gateway_server
        self._port_checker = port_checker
        self._gateway_initializer = gateway_initializer
        self._process_manager = process_manager
        self._status_checker = status_checker

        self._component_status: Dict[str, ComponentStatus] = {
            "gateway": ComponentStatus.STOPPED,
            "strategy": ComponentStatus.STOPPED,
            "order_executor": ComponentStatus.STOPPED,
        }

        self._startup_time: Optional[float] = None

    def start_trading_system(self) -> SystemStartupResult:
        """Start all trading system components.

        Returns:
            SystemStartupResult with status of each component
        """
        self._logger.log_info("Starting trading system...")

        try:
            # Start Gateway
            self._component_status["gateway"] = ComponentStatus.STARTING
            gateway_success = self._start_gateway()
            self._component_status["gateway"] = (
                ComponentStatus.RUNNING if gateway_success else ComponentStatus.ERROR
            )

            if not gateway_success:
                return SystemStartupResult(
                    success=False,
                    gateway_status=self._component_status["gateway"],
                    strategy_status=self._component_status["strategy"],
                    order_executor_status=self._component_status["order_executor"],
                    error_message="Failed to start Gateway",
                )

            # Wait for Gateway initialization
            time.sleep(3)

            # Start Strategy
            self._component_status["strategy"] = ComponentStatus.STARTING
            strategy_success = self._start_strategy()
            self._component_status["strategy"] = (
                ComponentStatus.RUNNING if strategy_success else ComponentStatus.ERROR
            )

            # Start Order Executor
            self._component_status["order_executor"] = ComponentStatus.STARTING
            order_executor_success = self._start_order_executor()
            self._component_status["order_executor"] = (
                ComponentStatus.RUNNING if order_executor_success else ComponentStatus.ERROR
            )

            # Record startup time if all components started
            if all(status == ComponentStatus.RUNNING for status in self._component_status.values()):
                self._startup_time = time.time()

            return SystemStartupResult(
                success=all(
                    status == ComponentStatus.RUNNING for status in self._component_status.values()
                ),
                gateway_status=self._component_status["gateway"],
                strategy_status=self._component_status["strategy"],
                order_executor_status=self._component_status["order_executor"],
            )

        except Exception as e:
            self._logger.log_error(f"Error starting trading system: {e}")
            return SystemStartupResult(
                success=False,
                gateway_status=self._component_status["gateway"],
                strategy_status=self._component_status["strategy"],
                order_executor_status=self._component_status["order_executor"],
                error_message=str(e),
            )

    def stop_trading_system(self) -> None:
        """Stop all trading system components gracefully."""
        self._logger.log_info("Stopping trading system...")

        try:
            # Stop Order Executor first
            if self._component_status["order_executor"] == ComponentStatus.RUNNING:
                self._component_status["order_executor"] = ComponentStatus.STOPPING
                self._process_manager.cleanup_processes()
                self._component_status["order_executor"] = ComponentStatus.STOPPED

            # Stop Strategy
            if self._component_status["strategy"] == ComponentStatus.RUNNING:
                self._component_status["strategy"] = ComponentStatus.STOPPING
                # Strategy cleanup handled by process manager
                self._component_status["strategy"] = ComponentStatus.STOPPED

            # Stop Gateway last
            if self._component_status["gateway"] == ComponentStatus.RUNNING:
                self._component_status["gateway"] = ComponentStatus.STOPPING
                self._gateway_server.stop()
                self._gateway_initializer.cleanup_zmq()
                self._component_status["gateway"] = ComponentStatus.STOPPED

            self._startup_time = None
            self._logger.log_info("Trading system stopped successfully")

        except Exception as e:
            self._logger.log_error(f"Error stopping trading system: {e}")

    def get_system_health(self) -> SystemHealth:
        """Get current health status of the system.

        Returns:
            SystemHealth object with current status
        """
        uptime = 0.0
        if self._startup_time:
            uptime = time.time() - self._startup_time

        is_healthy = all(
            status == ComponentStatus.RUNNING for status in self._component_status.values()
        )

        return SystemHealth(
            is_healthy=is_healthy,
            components=self._component_status.copy(),
            uptime_seconds=uptime,
            last_check_timestamp=time.time(),
        )

    def restart_component(self, component: str) -> bool:
        """Restart a specific component.

        Args:
            component: Name of component to restart

        Returns:
            True if restart successful, False otherwise
        """
        if component not in self._component_status:
            self._logger.log_error(f"Unknown component: {component}")
            return False

        self._logger.log_info(f"Restarting component: {component}")

        try:
            # Stop component
            if component == "gateway":
                self._gateway_server.stop()
                self._gateway_initializer.cleanup_zmq()
            elif component in ["strategy", "order_executor"]:
                # Process manager handles these
                pass

            self._component_status[component] = ComponentStatus.STOPPED

            # Start component
            if component == "gateway":
                success = self._start_gateway()
            elif component == "strategy":
                success = self._start_strategy()
            elif component == "order_executor":
                success = self._start_order_executor()
            else:
                success = False

            self._component_status[component] = (
                ComponentStatus.RUNNING if success else ComponentStatus.ERROR
            )

            return success

        except Exception as e:
            self._logger.log_error(f"Error restarting component {component}: {e}")
            self._component_status[component] = ComponentStatus.ERROR
            return False

    def _start_gateway(self) -> bool:
        """Start the Gateway component.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check port availability
            port_status = self._port_checker.check_port_availability()
            if not all(port_status.values()):
                self._logger.log_error("Required ports are not available")
                return False

            # Initialize market data components (ZMQ publisher and tick producer)
            if not self._gateway_initializer.initialize_components():
                self._logger.log_error("Failed to initialize gateway components")
                return False

            # Connect API callbacks to tick producer for real-time data
            if not self._gateway_initializer.connect_api_callbacks():
                self._logger.log_error("Failed to connect API callbacks")
                self._gateway_initializer.cleanup_zmq()
                return False

            # Start order execution server
            if not self._gateway_server.start():
                self._logger.log_error("Failed to start Gateway server")
                self._gateway_initializer.cleanup_zmq()
                return False

            self._logger.log_info("Gateway started successfully (market data + order execution)")
            return True

        except Exception as e:
            self._logger.log_error(f"Error starting Gateway: {e}")
            # Cleanup on error
            try:
                self._gateway_initializer.cleanup_zmq()
            except Exception:
                pass
            return False

    def _start_strategy(self) -> bool:
        """Start the Strategy component.

        Returns:
            True if successful, False otherwise
        """
        try:
            use_case = StartStrategyUseCase(
                logger=self._logger,
                process_manager_service=self._process_manager,
            )

            return use_case.execute()

        except Exception as e:
            self._logger.log_error(f"Error starting Strategy: {e}")
            return False

    def _start_order_executor(self) -> bool:
        """Start the Order Executor component.

        Returns:
            True if successful, False otherwise
        """
        try:
            use_case = StartOrderExecutorUseCase(
                logger=self._logger,
                process_manager_service=self._process_manager,
            )

            return use_case.execute()

        except Exception as e:
            self._logger.log_error(f"Error starting Order Executor: {e}")
            return False
