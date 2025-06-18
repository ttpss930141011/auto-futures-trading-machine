"""Domain Interfaces - Abstract interfaces for domain layer."""

from .exchange_api_interface import (
    ExchangeApiInterface,
    LoginCredentials,
    LoginResult,
    OrderRequest,
    OrderResult
)
from .exchange_converter_interface import ExchangeConverterInterface

__all__ = [
    'ExchangeApiInterface',
    'ExchangeConverterInterface',
    'LoginCredentials',
    'LoginResult',
    'OrderRequest',
    'OrderResult'
]