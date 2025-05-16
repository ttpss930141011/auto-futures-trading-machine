"""Start Strategy Use Case.

This use case handles starting the strategy component of the trading system.
"""

from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.process_manager_service_interface import ProcessManagerServiceInterface


class StartStrategyUseCase:
    """Use case for starting the strategy component of the trading system."""

    def __init__(
        self,
        logger: LoggerInterface,
        process_manager_service: ProcessManagerServiceInterface,
    ):
        """Initialize the use case.

        Args:
            logger: Logger for recording events
            process_manager_service: Service for managing processes
        """
        self.logger = logger
        self.process_manager_service = process_manager_service

    def execute(self) -> bool:
        """Execute the start strategy use case.

        Returns:
            bool: True if strategy was successfully started, False otherwise
        """
        try:
            self.logger.log_info("Starting strategy component...")
            
            # Use the process manager service to start the strategy
            success = self.process_manager_service.start_strategy()
            
            if success:
                self.logger.log_info("Strategy component started successfully")
            else:
                self.logger.log_error("Failed to start strategy component")
                
            return success
            
        except Exception as e:
            self.logger.log_error(f"Failed to start strategy: {str(e)}")
            return False