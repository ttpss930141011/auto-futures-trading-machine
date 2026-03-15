"""Service container for dependency injection.

This module provides the ServiceContainer class which manages all application
dependencies following the Dependency Inversion Principle.
"""

from src.app.cli_pfcf.config import Config
from src.domain.interfaces.exchange_api import ExchangeApiInterface
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
        exchange_api: ExchangeApiInterface,
    ) -> None:
        """Initialize the service container.

        Args:
            logger: Logger interface for application logging.
            config: Configuration instance for application settings.
            session_repository: Repository for managing user sessions.
            condition_repository: Repository for managing trading conditions.
            exchange_api: Exchange API interface for exchange operations.
        """
        self.logger = logger
        self.config = config
        self.session_repository = session_repository
        self.condition_repository = condition_repository
        self.exchange_api = exchange_api
