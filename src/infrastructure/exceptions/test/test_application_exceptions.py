"""Tests for application exceptions."""

import pytest

from src.infrastructure.exceptions.application_exceptions import (
    ApplicationException,
    ProcessException,
    BootstrapException,
    ControllerException,
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


class TestProcessException:
    """Test cases for ProcessException."""

    def test_process_exception_creation(self):
        """Test ProcessException can be created with message."""
        message = "Process operation failed"
        error = ProcessException(message)
        
        assert str(error) == message
        assert isinstance(error, ApplicationException)

    def test_process_exception_inheritance(self):
        """Test ProcessException inherits from ApplicationException."""
        error = ProcessException("test")
        assert isinstance(error, ApplicationException)
        assert isinstance(error, Exception)


class TestBootstrapException:
    """Test cases for BootstrapException."""

    def test_bootstrap_exception_creation(self):
        """Test BootstrapException can be created with message."""
        message = "Bootstrap failed"
        error = BootstrapException(message)
        
        assert str(error) == message
        assert isinstance(error, ApplicationException)

    def test_bootstrap_exception_inheritance(self):
        """Test BootstrapException inherits from ApplicationException."""
        error = BootstrapException("test")
        assert isinstance(error, ApplicationException)
        assert isinstance(error, Exception)


class TestControllerException:
    """Test cases for ControllerException."""

    def test_controller_exception_creation(self):
        """Test ControllerException can be created with message."""
        message = "Controller operation failed"
        error = ControllerException(message)
        
        assert str(error) == message
        assert isinstance(error, ApplicationException)

    def test_controller_exception_inheritance(self):
        """Test ControllerException inherits from ApplicationException."""
        error = ControllerException("test")
        assert isinstance(error, ApplicationException)
        assert isinstance(error, Exception)