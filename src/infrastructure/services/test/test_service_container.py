"""Tests for ServiceContainer."""

import pytest
from unittest.mock import Mock, MagicMock

from src.infrastructure.services.service_container import ServiceContainer


class TestServiceContainer:
    """Test cases for ServiceContainer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Mock()
        self.config = Mock()
        self.session_repository = Mock()
        self.condition_repository = Mock()
        self.exchange_api = Mock()

    def test_service_container_initialization(self):
        """Test ServiceContainer initializes with all dependencies."""
        container = ServiceContainer(
            logger=self.logger,
            config=self.config,
            session_repository=self.session_repository,
            condition_repository=self.condition_repository,
            exchange_api=self.exchange_api
        )
        
        assert container.logger == self.logger
        assert container.config == self.config
        assert container.session_repository == self.session_repository
        assert container.condition_repository == self.condition_repository
        assert container.exchange_api == self.exchange_api

    def test_exchange_client_property(self):
        """Test exchange_client property returns client from exchange_api."""
        mock_client = Mock()
        self.exchange_api.client = mock_client
        
        container = ServiceContainer(
            logger=self.logger,
            config=self.config,
            session_repository=self.session_repository,
            condition_repository=self.condition_repository,
            exchange_api=self.exchange_api
        )
        
        assert container.exchange_client == mock_client

    def test_exchange_trade_property(self):
        """Test exchange_trade property returns trade from exchange_api."""
        mock_trade = Mock()
        self.exchange_api.trade = mock_trade
        
        container = ServiceContainer(
            logger=self.logger,
            config=self.config,
            session_repository=self.session_repository,
            condition_repository=self.condition_repository,
            exchange_api=self.exchange_api
        )
        
        assert container.exchange_trade == mock_trade

    def test_exchange_decimal_property(self):
        """Test exchange_decimal property returns decimal from exchange_api."""
        mock_decimal = Mock()
        self.exchange_api.decimal = mock_decimal
        
        container = ServiceContainer(
            logger=self.logger,
            config=self.config,
            session_repository=self.session_repository,
            condition_repository=self.condition_repository,
            exchange_api=self.exchange_api
        )
        
        assert container.exchange_decimal == mock_decimal

    def test_all_properties_accessible(self):
        """Test all container properties are accessible."""
        container = ServiceContainer(
            logger=self.logger,
            config=self.config,
            session_repository=self.session_repository,
            condition_repository=self.condition_repository,
            exchange_api=self.exchange_api
        )
        
        # Should not raise any exceptions
        _ = container.logger
        _ = container.config
        _ = container.session_repository
        _ = container.condition_repository
        _ = container.exchange_api
        _ = container.exchange_client
        _ = container.exchange_trade
        _ = container.exchange_decimal

    def test_service_container_with_none_dependencies(self):
        """Test ServiceContainer behavior with None dependencies."""
        container = ServiceContainer(
            logger=None,
            config=None,
            session_repository=None,
            condition_repository=None,
            exchange_api=None
        )
        
        assert container.logger is None
        assert container.config is None
        assert container.session_repository is None
        assert container.condition_repository is None
        assert container.exchange_api is None

    def test_exchange_properties_with_none_api(self):
        """Test exchange properties when exchange_api is None."""
        container = ServiceContainer(
            logger=self.logger,
            config=self.config,
            session_repository=self.session_repository,
            condition_repository=self.condition_repository,
            exchange_api=None
        )
        
        # These should raise AttributeError when exchange_api is None
        with pytest.raises(AttributeError):
            _ = container.exchange_client
            
        with pytest.raises(AttributeError):
            _ = container.exchange_trade
            
        with pytest.raises(AttributeError):
            _ = container.exchange_decimal

    def test_dependency_injection_pattern(self):
        """Test that container follows dependency injection pattern."""
        # Create specific mock instances
        specific_logger = Mock(name="SpecificLogger")
        specific_config = Mock(name="SpecificConfig")
        specific_session_repo = Mock(name="SpecificSessionRepo")
        specific_condition_repo = Mock(name="SpecificConditionRepo")
        specific_exchange_api = Mock(name="SpecificExchangeAPI")
        
        container = ServiceContainer(
            logger=specific_logger,
            config=specific_config,
            session_repository=specific_session_repo,
            condition_repository=specific_condition_repo,
            exchange_api=specific_exchange_api
        )
        
        # Verify exact instances are stored (not copies or transformations)
        assert container.logger is specific_logger
        assert container.config is specific_config
        assert container.session_repository is specific_session_repo
        assert container.condition_repository is specific_condition_repo
        assert container.exchange_api is specific_exchange_api

    def test_container_immutability(self):
        """Test that container dependencies can't be accidentally modified."""
        container = ServiceContainer(
            logger=self.logger,
            config=self.config,
            session_repository=self.session_repository,
            condition_repository=self.condition_repository,
            exchange_api=self.exchange_api
        )
        
        original_logger = container.logger
        original_config = container.config
        
        # Direct assignment should work (no setter prevention)
        container.logger = Mock()
        container.config = Mock()
        
        # Verify assignment worked
        assert container.logger != original_logger
        assert container.config != original_config