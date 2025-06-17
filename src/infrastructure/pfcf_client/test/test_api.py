"""Tests for PFCF API."""

import pytest
from unittest.mock import Mock, patch

from src.infrastructure.pfcf_client.api import PFCFApi


class TestPFCFApi:
    """Test cases for PFCFApi."""

    @patch('src.infrastructure.pfcf_client.api.PFCFAPI')
    @patch('src.infrastructure.pfcf_client.api.DTrade')
    @patch('src.infrastructure.pfcf_client.api.Decimal')
    def test_init_creates_api_instance(self, mock_decimal, mock_dtrade, mock_pfcf):
        """Test PFCFApi initialization creates required instances."""
        mock_client = Mock()
        mock_pfcf.return_value = mock_client
        
        # Mock all the event handlers that get connected
        self._setup_mock_client_events(mock_client)
        
        api = PFCFApi()
        
        assert api.client == mock_client
        assert api.trade == mock_dtrade
        assert api.decimal == mock_decimal

    @patch('src.infrastructure.pfcf_client.api.PFCFAPI')
    def test_client_property_returns_client(self, mock_pfcf):
        """Test that client property returns the PFCF client."""
        mock_client = Mock()
        mock_pfcf.return_value = mock_client
        self._setup_mock_client_events(mock_client)
        
        api = PFCFApi()
        
        assert api.client == mock_client

    @patch('src.infrastructure.pfcf_client.api.PFCFAPI')
    @patch('src.infrastructure.pfcf_client.api.DTrade')
    def test_trade_property_returns_trade(self, mock_dtrade, mock_pfcf):
        """Test that trade property returns DTrade."""
        mock_client = Mock()
        mock_pfcf.return_value = mock_client
        self._setup_mock_client_events(mock_client)
        
        api = PFCFApi()
        
        assert api.trade == mock_dtrade

    @patch('src.infrastructure.pfcf_client.api.PFCFAPI')
    @patch('src.infrastructure.pfcf_client.api.Decimal')
    def test_decimal_property_returns_decimal(self, mock_decimal, mock_pfcf):
        """Test that decimal property returns Decimal."""
        mock_client = Mock()
        mock_pfcf.return_value = mock_client
        self._setup_mock_client_events(mock_client)
        
        api = PFCFApi()
        
        assert api.decimal == mock_decimal

    @patch('src.infrastructure.pfcf_client.api.PFCFAPI')
    def test_event_handlers_are_connected(self, mock_pfcf):
        """Test that all event handlers are properly connected."""
        mock_client = Mock()
        mock_pfcf.return_value = mock_client
        self._setup_mock_client_events(mock_client)
        
        api = PFCFApi()
        
        # Verify all event handlers were connected
        mock_client.PFCloginStatus.__iadd__.assert_called()
        mock_client.PFCErrorData.__iadd__.assert_called()
        mock_client.DQuoteLib.OnConnected.__iadd__.assert_called()
        mock_client.DQuoteLib.OnDisconnected.__iadd__.assert_called()
        mock_client.DTradeLib.OnReply.__iadd__.assert_called()
        mock_client.DTradeLib.OnMatch.__iadd__.assert_called()
        mock_client.DTradeLib.OnQueryReply.__iadd__.assert_called()
        mock_client.DTradeLib.OnQueryMatch.__iadd__.assert_called()
        mock_client.DAccountLib.OnConnected.__iadd__.assert_called()
        mock_client.DAccountLib.OnDisconnected.__iadd__.assert_called()
        mock_client.DAccountLib.OnMarginData.__iadd__.assert_called()
        mock_client.DAccountLib.OnMarginError.__iadd__.assert_called()
        mock_client.DAccountLib.OnPositionData.__iadd__.assert_called()
        mock_client.DAccountLib.OnPositionError.__iadd__.assert_called()
        mock_client.DAccountLib.OnUnLiquidationMainData.__iadd__.assert_called()
        mock_client.DAccountLib.OnUnLiquidationMainError.__iadd__.assert_called()
        mock_client.NoticeLib.OnConnected.__iadd__.assert_called()
        mock_client.NoticeLib.OnDisconnected.__iadd__.assert_called()

    @patch('src.infrastructure.pfcf_client.api.PFCFAPI')
    def test_api_properties_are_accessible(self, mock_pfcf):
        """Test that all API properties are accessible."""
        mock_client = Mock()
        mock_pfcf.return_value = mock_client
        self._setup_mock_client_events(mock_client)
        
        api = PFCFApi()
        
        # Should be able to access all properties without error
        assert hasattr(api, 'client')
        assert hasattr(api, 'trade')
        assert hasattr(api, 'decimal')

    @patch('src.infrastructure.pfcf_client.api.PFCFAPI')
    def test_api_handles_dll_manager_exception(self, mock_pfcf):
        """Test API handles DLL manager exceptions gracefully."""
        mock_pfcf.side_effect = Exception("DLL loading failed")
        
        # Should propagate the exception
        with pytest.raises(Exception, match="DLL loading failed"):
            PFCFApi()

    @patch('src.infrastructure.pfcf_client.api.PFCFAPI')
    def test_multiple_api_instances(self, mock_pfcf):
        """Test that multiple API instances can be created."""
        mock_client1 = Mock()
        mock_client2 = Mock()
        mock_pfcf.side_effect = [mock_client1, mock_client2]
        
        self._setup_mock_client_events(mock_client1)
        self._setup_mock_client_events(mock_client2)
        
        api1 = PFCFApi()
        api2 = PFCFApi()
        
        assert api1.client == mock_client1
        assert api2.client == mock_client2
        assert api1.client != api2.client

    @patch('src.infrastructure.pfcf_client.api.PFCFAPI')
    def test_api_initialization_with_mock_dll(self, mock_pfcf):
        """Test API initialization works with mock DLL."""
        mock_client = Mock()
        mock_pfcf.return_value = mock_client
        self._setup_mock_client_events(mock_client)
        
        # Should complete initialization without errors
        api = PFCFApi()
        
        # Verify initialization completed
        assert api.client is not None
        assert api.trade is not None
        assert api.decimal is not None

    def _setup_mock_client_events(self, mock_client):
        """Set up all required mock events for the client."""
        # Main client events
        mock_client.PFCloginStatus = Mock()
        mock_client.PFCErrorData = Mock()
        
        # DQuoteLib events
        mock_client.DQuoteLib = Mock()
        mock_client.DQuoteLib.OnConnected = Mock()
        mock_client.DQuoteLib.OnDisconnected = Mock()
        
        # DTradeLib events
        mock_client.DTradeLib = Mock()
        mock_client.DTradeLib.OnReply = Mock()
        mock_client.DTradeLib.OnMatch = Mock()
        mock_client.DTradeLib.OnQueryReply = Mock()
        mock_client.DTradeLib.OnQueryMatch = Mock()
        
        # DAccountLib events
        mock_client.DAccountLib = Mock()
        mock_client.DAccountLib.OnConnected = Mock()
        mock_client.DAccountLib.OnDisconnected = Mock()
        mock_client.DAccountLib.OnMarginData = Mock()
        mock_client.DAccountLib.OnMarginError = Mock()
        mock_client.DAccountLib.OnPositionData = Mock()
        mock_client.DAccountLib.OnPositionError = Mock()
        mock_client.DAccountLib.OnUnLiquidationMainData = Mock()
        mock_client.DAccountLib.OnUnLiquidationMainError = Mock()
        
        # NoticeLib events
        mock_client.NoticeLib = Mock()
        mock_client.NoticeLib.OnConnected = Mock()
        mock_client.NoticeLib.OnDisconnected = Mock()