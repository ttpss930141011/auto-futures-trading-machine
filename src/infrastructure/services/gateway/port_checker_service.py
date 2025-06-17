"""Service for checking port availability for ZMQ components.

This service provides functionality to check if the required ports are available
for ZeroMQ message broker components.
"""

import socket
from contextlib import closing
from typing import Dict

from src.app.cli_pfcf.config import Config
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.port_checker_service_interface import PortCheckerServiceInterface


class PortCheckerService(PortCheckerServiceInterface):
    """Service for checking port availability for network components."""

    def __init__(self, config: Config, logger: LoggerInterface):
        """Initialize the port checker service.

        Args:
            config: Application configuration with port information
            logger: Logger for recording events
        """
        self.config = config
        self.logger = logger

    def check_port_availability(self) -> Dict[str, bool]:
        """Check if the required ports are available.

        Returns:
            Dict[str, bool]: Dictionary with port numbers as keys and availability as values
        """
        ports_to_check = {
            self.config.ZMQ_TICK_PORT: "Publisher port",
            self.config.ZMQ_SIGNAL_PORT: "Signal Puller port",
        }
        results = {}

        for port, description in ports_to_check.items():
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                try:
                    sock.bind(("127.0.0.1", port))
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.logger.log_info(f"Port {port} ({description}) is available")
                    results[port] = True
                except socket.error:
                    self.logger.log_error(f"Port {port} ({description}) is already in use")
                    results[port] = False

        return results
