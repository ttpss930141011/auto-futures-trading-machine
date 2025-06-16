"""Application-level exceptions."""


class ApplicationException(Exception):
    """Base exception for application-level errors."""


class ProcessException(ApplicationException):
    """Exception raised during process operations."""


class BootstrapException(ApplicationException):
    """Exception raised during application bootstrap."""


class ControllerException(ApplicationException):
    """Exception raised in controller operations."""
