"""Start Order Executor Use Case.

This use case handles starting the order executor component of the trading system.
"""

from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.process_manager_service_interface import ProcessManagerServiceInterface


class StartOrderExecutorUseCase:
    """Use case for starting the order executor component of the trading system."""

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
        """Execute the start order executor use case.

        Returns:
            bool: True if order executor was successfully started, False otherwise
        """
        try:
            self.logger.log_info("Starting order executor component...")
            
            # Use the process manager service to start the order executor
            success = self.process_manager_service.start_order_executor()
            
            if success:
                self.logger.log_info("Order executor component started successfully")
            else:
                self.logger.log_error("Failed to start order executor component")
                
            return success
            
        except Exception as e:
            self.logger.log_error(f"Failed to start order executor: {str(e)}")
            return False