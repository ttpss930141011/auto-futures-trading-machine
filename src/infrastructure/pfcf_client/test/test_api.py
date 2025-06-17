"""Tests for PFCF API."""

import pytest
from src.infrastructure.pfcf_client.api import PFCFApi


class TestPFCFApi:
    """Test cases for PFCFApi."""

    def test_init_creates_api_instance(self):
        """Test PFCFApi initialization creates required instances."""
        # Use the real mock DLL instead of patching
        api = PFCFApi()
        
        # Should create API instance successfully
        assert api.client is not None
        assert api.trade is not None  
        assert api.decimal is not None

    def test_client_property_accessible(self):
        """Test that client property is accessible."""
        api = PFCFApi()
        
        # Should be able to access client
        assert hasattr(api, 'client')
        assert api.client is not None

    def test_trade_property_accessible(self):
        """Test that trade property is accessible."""
        api = PFCFApi()
        
        # Should be able to access trade
        assert hasattr(api, 'trade')
        assert api.trade is not None

    def test_decimal_property_accessible(self):
        """Test that decimal property is accessible."""
        api = PFCFApi()
        
        # Should be able to access decimal
        assert hasattr(api, 'decimal')
        assert api.decimal is not None

    def test_api_properties_are_accessible(self):
        """Test that all API properties are accessible."""
        api = PFCFApi()
        
        # Should be able to access all properties without error
        assert hasattr(api, 'client')
        assert hasattr(api, 'trade')
        assert hasattr(api, 'decimal')

    def test_multiple_api_instances(self):
        """Test that multiple API instances can be created."""
        api1 = PFCFApi()
        api2 = PFCFApi()
        
        # Both should be valid instances
        assert api1.client is not None
        assert api2.client is not None
        assert api1.trade is not None
        assert api2.trade is not None

    def test_api_initialization_with_mock_dll(self):
        """Test API initialization works with mock DLL."""
        # Should complete initialization without errors
        api = PFCFApi()
        
        # Verify initialization completed
        assert api.client is not None
        assert api.trade is not None
        assert api.decimal is not None

    def test_client_has_expected_structure(self):
        """Test that client has expected event structure."""
        api = PFCFApi()
        
        # Client should have main components
        assert hasattr(api.client, 'PFCloginStatus')
        assert hasattr(api.client, 'PFCErrorData')
        assert hasattr(api.client, 'DQuoteLib')
        assert hasattr(api.client, 'DTradeLib')
        assert hasattr(api.client, 'DAccountLib')
        assert hasattr(api.client, 'NoticeLib')

    def test_dll_libs_have_event_handlers(self):
        """Test that DLL libraries have event handlers."""
        api = PFCFApi()
        
        # Check DQuoteLib events
        assert hasattr(api.client.DQuoteLib, 'OnConnected')
        assert hasattr(api.client.DQuoteLib, 'OnDisconnected')
        
        # Check DTradeLib events
        assert hasattr(api.client.DTradeLib, 'OnReply')
        assert hasattr(api.client.DTradeLib, 'OnMatch')
        
        # Check DAccountLib events
        assert hasattr(api.client.DAccountLib, 'OnPositionData')
        assert hasattr(api.client.DAccountLib, 'OnPositionError')

    def test_event_handlers_support_iadd(self):
        """Test that event handlers support += operator."""
        api = PFCFApi()
        
        # Should be able to add event handlers
        handler = lambda x: x
        
        # These should not raise exceptions (using mock events)
        try:
            api.client.PFCloginStatus += handler
            api.client.DQuoteLib.OnConnected += handler
            api.client.DTradeLib.OnReply += handler
            # Test passes if no exception is raised
            assert True
        except Exception as e:
            pytest.fail(f"Event handler assignment should work: {e}")