"""Start Application Use Case.


This use case handles the verification of prerequisites and preparation for application startup.
"""

from typing import Dict, Any


from src.interactor.interfaces.services.status_checker import StatusCheckerInterface

from src.interactor.interfaces.logger.logger import LoggerInterface


class ApplicationStartupStatusUseCase:
    """Use case for starting the application with all prerequisites checks."""

    def __init__(self, logger: LoggerInterface, status_checker: StatusCheckerInterface):
        """Initialize the use case.


        Args:

            logger: Logger for recording events

            status_checker: Status checker for verifying system prerequisites
        """

        self.logger = logger

        self.status_checker = status_checker

    def execute(self) -> Dict[str, bool]:
        """Execute the start application use case.


        Checks all system prerequisites and returns a status summary.


        Returns:

            Dict[str, bool]: Summary of system status
        """

        self.logger.log_info("Starting application - checking prerequisites")

        # Check all prerequisites

        status_summary = self.status_checker.get_status_summary()

        # Log the status

        self._log_status_summary(status_summary)

        return status_summary

    def _log_status_summary(self, status_summary: Dict[str, bool]) -> None:
        """Log the status summary.


        Args:

            status_summary: Dictionary with status check results
        """

        self.logger.log_info("System status summary:")

        for status_name, status_value in status_summary.items():

            status_text = "OK" if status_value else "NOT READY"

            self.logger.log_info(f"  {status_name}: {status_text}")

        if all(status_summary.values()):

            self.logger.log_info("All prerequisites met. System ready to start.")

        else:

            missing_prereqs = [name for name, value in status_summary.items() if not value]

            self.logger.log_warning(
                f"System not ready. Missing prerequisites: {', '.join(missing_prereqs)}"
            )
