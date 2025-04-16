
from src.interactor.interfaces.services.status_checker import StatusCheckerInterface
from src.infrastructure.services.service_container import ServiceContainer
from typing import Dict

class StatusChecker(StatusCheckerInterface):
    """Implementation of status checker to verify preconditions."""
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.logger = service_container.logger
        self.session_repository = service_container.session_repository
        self.condition_repository = service_container.condition_repository
    
    def is_user_logged_in(self) -> bool:
        """Check if user is logged in."""
        return self.session_repository.is_user_logged_in()
    
    def is_item_registered(self) -> bool:
        """Check if item is registered."""
        return self.session_repository.get_item_code() is not None
    
    def is_order_account_selected(self) -> bool:
        """Check if order account is selected."""
        return self.session_repository.get_order_account() is not None
    
    def has_conditions(self) -> bool:
        """Check if there are any conditions defined."""
        return len(self.condition_repository.get_all()) > 0
    
    def get_status_summary(self) -> Dict[str, bool]:
        """Get a summary of all status checks."""
        return {
            "logged_in": self.is_user_logged_in(),
            "item_registered": self.is_item_registered(),
            "order_account_selected": self.is_order_account_selected(),
            "has_conditions": self.has_conditions()
        }
