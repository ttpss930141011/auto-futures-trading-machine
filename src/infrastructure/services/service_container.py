from src.app.cli_pfcf.config import Config
from src.infrastructure.repositories.condition_in_memory_repository import ConditionInMemoryRepository
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


class ServiceContainer:
    def __init__(self, logger: LoggerInterface, config: Config,
                 session_repository: SessionRepositoryInterface,
                 condition_repository: ConditionInMemoryRepository):
        self.logger = logger
        self.config = config
        self.session_repository = session_repository
        self.condition_repository = condition_repository
