"""Status Checker Interface for system readiness verification.

Defines the interface for checking the status of various system components.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class StatusCheckerInterface(ABC):
    """Interface for checking the status of system prerequisites."""
    
    @abstractmethod
    def is_user_logged_in(self) -> bool:
        """Check if user is logged in.
        
        Returns:
            bool: True if user is logged in, False otherwise
        """
        pass
    
    @abstractmethod
    def is_item_registered(self) -> bool:
        """Check if item is registered.
        
        Returns:
            bool: True if item is registered, False otherwise
        """
        pass
    
    @abstractmethod
    def is_order_account_selected(self) -> bool:
        """Check if order account is selected.
        
        Returns:
            bool: True if order account is selected, False otherwise
        """
        pass
    
    @abstractmethod
    def has_conditions(self) -> bool:
        """Check if there are any conditions defined.
        
        Returns:
            bool: True if conditions exist, False otherwise
        """
        pass
    
    @abstractmethod
    def get_status_summary(self) -> Dict[str, bool]:
        """Get a summary of all status checks.
        
        Returns:
            Dict[str, bool]: Dictionary with status check results
        """
        pass