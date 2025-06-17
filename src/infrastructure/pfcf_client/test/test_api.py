"""Tests for PFCF API."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.infrastructure.pfcf_client.api import PFCFApi


class TestPFCFApi:
    """Test cases for PFCFApi."""

    def setup_method(self):
        """Set up test fixtures."""
        pass

    def test_init_creates_api_instance(self):
        """Test initialization creates API instance."""
        api = PFCFApi()
        
        assert hasattr(api, 'client')
        assert hasattr(api, 'trade')
        assert hasattr(api, 'decimal')

    @patch('src.infrastructure.pfcf_client.api.DLLManager')
    def test_client_property_returns_client(self, mock_dll_manager):
        """Test client property returns client instance."""
        mock_client = Mock()
        mock_dll_manager.return_value.client = mock_client
        
        api = PFCFApi()
        
        assert api.client == mock_client

    @patch('src.infrastructure.pfcf_client.api.DLLManager')
    def test_trade_property_returns_trade(self, mock_dll_manager):
        """Test trade property returns trade instance."""
        mock_trade = Mock()
        mock_dll_manager.return_value.trade = mock_trade
        
        api = PFCFApi()
        
        assert api.trade == mock_trade

    @patch('src.infrastructure.pfcf_client.api.DLLManager')
    def test_decimal_property_returns_decimal(self, mock_dll_manager):
        """Test decimal property returns decimal instance."""
        mock_decimal = Mock()
        mock_dll_manager.return_value.decimal = mock_decimal
        
        api = PFCFApi()
        
        assert api.decimal == mock_decimal

    @patch('src.infrastructure.pfcf_client.api.DLLManager')
    def test_api_initialization_with_dll_manager(self, mock_dll_manager):
        """Test API initializes with DLL manager."""
        mock_dll_instance = Mock()
        mock_dll_manager.return_value = mock_dll_instance
        
        api = PFCFApi()
        
        # Verify DLLManager was called
        mock_dll_manager.assert_called_once()
        
        # Verify the DLL manager instance is stored
        assert api._dll_manager == mock_dll_instance

    def test_api_properties_are_accessible(self):
        """Test all API properties are accessible."""
        api = PFCFApi()
        
        # These should not raise exceptions
        try:
            _ = api.client
            _ = api.trade  
            _ = api.decimal
        except Exception as e:
            pytest.fail(f"API properties should be accessible: {e}")

    @patch('src.infrastructure.pfcf_client.api.DLLManager')
    def test_api_handles_dll_manager_exception(self, mock_dll_manager):
        """Test API handles DLL manager initialization exceptions."""
        mock_dll_manager.side_effect = Exception("DLL initialization failed")
        
        # This should still work even if DLL initialization fails
        # The actual error handling depends on the DLLManager implementation
        with pytest.raises(Exception, match="DLL initialization failed"):
            PFCFApi()

    @patch('src.infrastructure.pfcf_client.api.DLLManager')
    def test_multiple_api_instances(self, mock_dll_manager):
        """Test multiple API instances can be created."""
        mock_dll_manager.return_value = Mock()
        
        api1 = PFCFApi()
        api2 = PFCFApi()
        
        # Each should have its own DLL manager
        assert mock_dll_manager.call_count == 2
        assert api1._dll_manager != api2._dll_manager