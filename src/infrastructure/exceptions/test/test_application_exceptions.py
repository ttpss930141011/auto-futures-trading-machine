"""Tests for application exceptions."""

import pytest

from src.infrastructure.exceptions.application_exceptions import (
    ApplicationException,
    ConfigurationError,
    InitializationError,
    ServiceUnavailableError,
)


class TestApplicationException:
    """Test cases for ApplicationException base class."""

    def test_application_exception_creation(self):
        """Test ApplicationException can be created with message."""
        message = "Test application error"
        exception = ApplicationException(message)
        
        assert str(exception) == message
        assert isinstance(exception, Exception)

    def test_application_exception_inheritance(self):
        """Test ApplicationException inherits from Exception."""
        exception = ApplicationException("test")
        assert isinstance(exception, Exception)


class TestConfigurationError:
    """Test cases for ConfigurationError."""

    def test_configuration_error_creation(self):
        """Test ConfigurationError can be created with message."""
        message = "Invalid configuration"
        error = ConfigurationError(message)
        
        assert str(error) == message
        assert isinstance(error, ApplicationException)

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inherits from ApplicationException."""
        error = ConfigurationError("test")
        assert isinstance(error, ApplicationException)
        assert isinstance(error, Exception)


class TestInitializationError:
    """Test cases for InitializationError."""

    def test_initialization_error_creation(self):
        """Test InitializationError can be created with message."""
        message = "Initialization failed"
        error = InitializationError(message)
        
        assert str(error) == message
        assert isinstance(error, ApplicationException)

    def test_initialization_error_inheritance(self):
        """Test InitializationError inherits from ApplicationException."""
        error = InitializationError("test")
        assert isinstance(error, ApplicationException)
        assert isinstance(error, Exception)


class TestServiceUnavailableError:
    """Test cases for ServiceUnavailableError."""

    def test_service_unavailable_error_creation(self):
        """Test ServiceUnavailableError can be created with message."""
        message = "Service is unavailable"
        error = ServiceUnavailableError(message)
        
        assert str(error) == message
        assert isinstance(error, ApplicationException)

    def test_service_unavailable_error_inheritance(self):
        """Test ServiceUnavailableError inherits from ApplicationException."""
        error = ServiceUnavailableError("test")
        assert isinstance(error, ApplicationException)
        assert isinstance(error, Exception)