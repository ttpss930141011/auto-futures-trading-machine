"""Tests for PFCF DLL stub module."""

import pytest


class TestDLLModule:
    """Test cases for DLL module imports."""

    def test_dll_module_imports_successfully(self):
        """Test that DLL module can be imported without errors."""
        import src.infrastructure.pfcf_client.dll as dll_module
        assert dll_module is not None

    def test_dll_exports_required_classes(self):
        """Test that DLL module exports required classes."""
        import src.infrastructure.pfcf_client.dll as dll_module
        
        # Check that main export classes exist
        assert hasattr(dll_module, 'PFCFAPI')
        assert hasattr(dll_module, 'DTrade')
        assert hasattr(dll_module, 'Decimal')

    def test_pfcfapi_can_be_instantiated(self):
        """Test that PFCFAPI can be instantiated."""
        import src.infrastructure.pfcf_client.dll as dll_module
        
        api = dll_module.PFCFAPI()
        assert api is not None

    def test_mock_classes_functionality(self):
        """Test basic mock class functionality."""
        import src.infrastructure.pfcf_client.dll as dll_module
        
        # Test MockEvent
        event = dll_module.MockEvent()
        handler = lambda x: x
        
        # These should not raise exceptions
        result1 = event.__iadd__(handler)
        result2 = event.__isub__(handler)
        
        assert result1 == event
        assert result2 == event

    def test_mock_api_structure(self):
        """Test MockPFCFAPI has expected structure."""
        import src.infrastructure.pfcf_client.dll as dll_module
        
        api = dll_module.MockPFCFAPI()
        
        # Check that API has expected attributes
        assert hasattr(api, 'PFCloginStatus')
        assert hasattr(api, 'PFCErrorData')
        assert hasattr(api, 'DQuoteLib')
        assert hasattr(api, 'DTradeLib')
        assert hasattr(api, 'DAccountLib')
        assert hasattr(api, 'NoticeLib')

    def test_mock_lib_structure(self):
        """Test MockLib has expected event handlers."""
        import src.infrastructure.pfcf_client.dll as dll_module
        
        lib = dll_module.MockLib()
        
        # Check that lib has expected event handlers
        expected_events = [
            'OnConnected', 'OnDisconnected', 'OnReply', 'OnMatch',
            'OnQueryReply', 'OnQueryMatch', 'OnMarginData', 'OnMarginError',
            'OnPositionData', 'OnPositionError', 'OnUnLiquidationMainData',
            'OnUnLiquidationMainError'
        ]
        
        for event_name in expected_events:
            assert hasattr(lib, event_name)