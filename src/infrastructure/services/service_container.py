"""Service container for dependency injection.

This module provides the ServiceContainer class which manages all application
dependencies following the Dependency Inversion Principle.
"""

from src.app.cli_pfcf.config import Config
from src.domain.interfaces.exchange_api_interface import ExchangeApiInterface
from src.infrastructure.pfcf_client.api import PFCFApi
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


class ServiceContainer:
    """Container for all application services and dependencies.

    This class follows the Dependency Inversion Principle by managing
    dependencies through constructor injection and providing a centralized
    location for service access.
    """

    def __init__(
        self,
        logger: LoggerInterface,
        config: Config,
        session_repository: SessionRepositoryInterface,
        condition_repository: ConditionRepositoryInterface,
        exchange_api: PFCFApi,
        exchange_api_v2: ExchangeApiInterface = None,
    ) -> None:
        """Initialize the service container.

        Args:
            logger: Logger interface for application logging.
            config: Configuration instance for application settings.
            session_repository: Repository for managing user sessions.
            condition_repository: Repository for managing trading conditions.
            exchange_api: PFCF API instance for exchange operations (legacy).
            exchange_api_v2: New abstracted exchange API interface.
        """
        self.logger = logger
        self.config = config
        self.session_repository = session_repository
        self.condition_repository = condition_repository
        self.exchange_api = exchange_api  # Legacy PFCF API
        self.exchange_api_v2 = exchange_api_v2  # New abstracted API

    @property
    def exchange_client(self):
        """Get the exchange client from the API."""
        return self.exchange_api.client

    @property
    def exchange_trade(self):
        """Get the exchange trade interface from the API."""
        return self.exchange_api.trade

    @property
    def exchange_decimal(self):
        """Get the exchange decimal interface from the API."""
        return self.exchange_api.decimal
