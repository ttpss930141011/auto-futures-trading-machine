"""Errors related to DLL Gateway operations."""

from typing import Optional


class DllGatewayError(Exception):
    """Base exception for DLL Gateway errors."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        """Initialize DLL Gateway error.

        Args:
            message: Human-readable error message.
            error_code: Optional error code for programmatic handling.
        """
        super().__init__(message)
        self.error_code = error_code


class DllGatewayConnectionError(DllGatewayError):
    """Exception raised when DLL Gateway is not accessible."""


class DllGatewayTimeoutError(DllGatewayError):
    """Exception raised when DLL Gateway operation times out."""


class InvalidOrderError(DllGatewayError):
    """Exception raised when order request is invalid."""


class ExchangeApiError(DllGatewayError):
    """Exception raised when exchange API returns an error."""
