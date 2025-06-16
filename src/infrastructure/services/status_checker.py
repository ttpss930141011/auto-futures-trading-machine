"""Status Checker Service.

This service provides functionality to check various system prerequisites.
"""

from typing import Dict

from src.interactor.interfaces.services.status_checker import StatusCheckerInterface
from src.infrastructure.services.service_container import ServiceContainer


class StatusChecker(StatusCheckerInterface):
    """Implementation of status checker to verify preconditions."""

    def __init__(self, service_container: ServiceContainer):
        """Initialize the status checker service.

        Args:
            service_container: Container with all services and dependencies
        """
        self.service_container = service_container
        self.logger = service_container.logger
        self.session_repository = service_container.session_repository
        self.condition_repository = service_container.condition_repository

    def is_user_logged_in(self) -> bool:
        """Check if user is logged in.

        Returns:
            bool: True if user is logged in, False otherwise
        """
        return self.session_repository.is_user_logged_in()

    def is_item_registered(self) -> bool:
        """Check if item is registered.

        Returns:
            bool: True if item is registered, False otherwise
        """
        return self.session_repository.get_item_code() is not None

    def is_order_account_selected(self) -> bool:
        """Check if order account is selected.

        Returns:
            bool: True if order account is selected, False otherwise
        """
        return self.session_repository.get_order_account() is not None

    def has_conditions(self) -> bool:
        """Check if there are any conditions defined.

        Returns:
            bool: True if there are conditions defined, False otherwise
        """
        return len(self.condition_repository.get_all()) > 0

    def get_status_summary(self) -> Dict[str, bool]:
        """Get a summary of all status checks.

        Returns:
            Dict[str, bool]: Dictionary with status check names as keys and results as values
        """
        return {
            "logged_in": self.is_user_logged_in(),
            "item_registered": self.is_item_registered(),
            "order_account_selected": self.is_order_account_selected(),
            "has_conditions": self.has_conditions()
        }
