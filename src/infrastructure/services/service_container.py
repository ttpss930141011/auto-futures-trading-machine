"""Service container for dependency injection."""

from dataclasses import dataclass

from src.app.cli_pfcf.config import Config
from src.domain.interfaces.exchange_api import ExchangeApiInterface
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


@dataclass(frozen=True)
class ServiceContainer:
    """Immutable bag of shared application dependencies.

    Passed to controllers and use cases so they can reach shared services
    without wiring every dependency through multiple layers.
    """

    logger: LoggerInterface
    config: Config
    session_repository: SessionRepositoryInterface
    condition_repository: ConditionRepositoryInterface
    exchange_api: ExchangeApiInterface
