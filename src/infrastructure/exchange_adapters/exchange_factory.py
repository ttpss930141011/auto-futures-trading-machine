"""Exchange Factory - Creates appropriate exchange API implementation based on configuration."""

import os
from enum import Enum
from typing import Optional

from src.domain.interfaces.exchange_api_interface import ExchangeApiInterface
from src.infrastructure.exchange_adapters.pfcf_exchange_api import PFCFExchangeApi
from src.infrastructure.services.service_container import ServiceContainer


class ExchangeProvider(Enum):
    """Supported exchange providers."""
    
    PFCF = "PFCF"  # Taiwan Unified Futures
    YUANTA = "YUANTA"  # Yuanta Securities (future implementation)
    CAPITAL = "CAPITAL"  # Capital Futures (future implementation)
    SIMULATOR = "SIMULATOR"  # For testing


class ExchangeFactory:
    """Factory for creating exchange API implementations."""
    
    @staticmethod
    def create_exchange_api(
        provider: Optional[str] = None,
        service_container: Optional[ServiceContainer] = None
    ) -> ExchangeApiInterface:
        """Create exchange API based on provider.
        
        Args:
            provider: Exchange provider name. If None, reads from environment.
            service_container: Service container with dependencies.
            
        Returns:
            Exchange API implementation.
            
        Raises:
            ValueError: If provider is not supported.
        """
        # Get provider from parameter or environment
        if provider is None:
            provider = os.getenv("EXCHANGE_PROVIDER", "PFCF")
        
        # Convert to enum
        try:
            provider_enum = ExchangeProvider(provider.upper())
        except ValueError:
            raise ValueError(f"Unsupported exchange provider: {provider}")
        
        # Create appropriate implementation
        if provider_enum == ExchangeProvider.PFCF:
            if service_container is None:
                raise ValueError("Service container required for PFCF provider")
            return PFCFExchangeApi(service_container)
        
        elif provider_enum == ExchangeProvider.YUANTA:
            # Future implementation
            raise NotImplementedError("Yuanta Securities adapter not yet implemented")
        
        elif provider_enum == ExchangeProvider.CAPITAL:
            # Future implementation
            raise NotImplementedError("Capital Futures adapter not yet implemented")
        
        elif provider_enum == ExchangeProvider.SIMULATOR:
            # For testing - create a simulator
            from src.infrastructure.exchange_adapters.simulator_exchange_api import SimulatorExchangeApi
            return SimulatorExchangeApi()
        
        else:
            raise ValueError(f"Unknown exchange provider: {provider}")
    
    @staticmethod
    def get_supported_providers() -> list[str]:
        """Get list of supported exchange providers."""
        return [provider.value for provider in ExchangeProvider]
    
    @staticmethod
    def is_provider_supported(provider: str) -> bool:
        """Check if a provider is supported."""
        try:
            ExchangeProvider(provider.upper())
            return True
        except ValueError:
            return False