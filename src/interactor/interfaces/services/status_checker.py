"""Status Checker Interface.

This module defines the interface for the status checker service.
"""

from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class StatusCheckerInterface(Protocol):
    """Interface for the status checker service."""
    
    def is_user_logged_in(self) -> bool:
        """Check if user is logged in."""
        ...
    
    def is_item_registered(self) -> bool:
        """Check if item is registered."""
        ...
    
    def is_order_account_selected(self) -> bool:
        """Check if order account is selected."""
        ...
    
    def has_conditions(self) -> bool:
        """Check if there are any conditions defined."""
        ...
    
    def get_status_summary(self) -> Dict[str, bool]:
        """Get a summary of all status checks."""
        ...