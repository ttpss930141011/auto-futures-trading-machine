"""Tests for DLL Gateway error classes.

This module tests the custom exception classes defined for DLL Gateway operations.
"""

import pytest
from src.interactor.errors.dll_gateway_errors import (
    DllGatewayError,
    DllGatewayConnectionError,
    DllGatewayTimeoutError,
    InvalidOrderError,
    ExchangeApiError,
)


class TestDllGatewayErrors:
    """Test suite for DLL Gateway error classes."""

    def test_dll_gateway_error_basic(self):
        """Test basic DLL Gateway error creation."""
        error_message = "Gateway service unavailable"
        error = DllGatewayError(error_message)
        
        assert str(error) == error_message
        assert error.error_code is None

    def test_dll_gateway_error_with_code(self):
        """Test DLL Gateway error with error code."""
        error_message = "Authentication failed"
        error_code = "AUTH_FAILED"
        error = DllGatewayError(error_message, error_code)
        
        assert str(error) == error_message
        assert error.error_code == error_code

    def test_dll_gateway_connection_error(self):
        """Test DLL Gateway connection error."""
        error_message = "Cannot connect to gateway server"
        error = DllGatewayConnectionError(error_message)
        
        assert str(error) == error_message
        assert isinstance(error, DllGatewayError)

    def test_dll_gateway_timeout_error(self):
        """Test DLL Gateway timeout error."""
        error_message = "Request timeout after 5000ms"
        error = DllGatewayTimeoutError(error_message)
        
        assert str(error) == error_message
        assert isinstance(error, DllGatewayError)

    def test_invalid_order_error(self):
        """Test Invalid Order error."""
        error_message = "Missing required field: order_account"
        error = InvalidOrderError(error_message)
        
        assert str(error) == error_message
        assert isinstance(error, DllGatewayError)

    def test_exchange_api_error(self):
        """Test Exchange API error."""
        error_message = "Exchange API returned error: Invalid symbol"
        error_code = "INVALID_SYMBOL"
        error = ExchangeApiError(error_message, error_code)
        
        assert str(error) == error_message
        assert error.error_code == error_code
        assert isinstance(error, DllGatewayError)

    def test_error_inheritance_chain(self):
        """Test that all errors inherit from DllGatewayError."""
        errors = [
            DllGatewayConnectionError("test"),
            DllGatewayTimeoutError("test"),
            InvalidOrderError("test"),
            ExchangeApiError("test"),
        ]
        
        for error in errors:
            assert isinstance(error, DllGatewayError)
            assert isinstance(error, Exception)

    def test_error_raising_and_catching(self):
        """Test raising and catching specific error types."""
        # Test specific error catching
        with pytest.raises(DllGatewayConnectionError):
            raise DllGatewayConnectionError("Connection failed")
        
        # Test catching base error
        with pytest.raises(DllGatewayError):
            raise DllGatewayTimeoutError("Timeout occurred")
        
        # Test catching Exception
        with pytest.raises(Exception):
            raise InvalidOrderError("Invalid order")

    def test_error_code_propagation(self):
        """Test that error codes are properly maintained."""
        test_cases = [
            (DllGatewayError("msg", "CODE1"), "CODE1"),
            (DllGatewayConnectionError("msg", "CODE2"), "CODE2"),
            (ExchangeApiError("msg", "CODE3"), "CODE3"),
        ]
        
        for error, expected_code in test_cases:
            assert error.error_code == expected_code