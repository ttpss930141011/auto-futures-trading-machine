from src.app.cli_pfcf.config import Config
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


class ServiceContainer:
    def __init__(
        self,
        logger: LoggerInterface,
        config: Config,
        session_repository: SessionRepositoryInterface,
        condition_repository: ConditionRepositoryInterface,
    ):
        self.logger = logger
        self.config = config
        self.session_repository = session_repository
        self.condition_repository = condition_repository
