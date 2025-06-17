"""Tests for PFCF DLL Manager."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.infrastructure.pfcf_client.dll import DLLManager


class TestDLLManager:
    """Test cases for DLLManager."""

    def setup_method(self):
        """Set up test fixtures."""
        pass

    @patch('os.path.exists')
    @patch('ctypes.CDLL')
    def test_init_loads_dll_successfully(self, mock_cdll, mock_path_exists):
        """Test DLL manager initializes and loads DLL successfully."""
        mock_path_exists.return_value = True
        mock_dll = Mock()
        mock_cdll.return_value = mock_dll
        
        # Mock DLL functions
        mock_dll.CreateClient = Mock()
        mock_dll.CreateTrade = Mock()
        mock_dll.CreateDecimal = Mock()
        
        manager = DLLManager()
        
        # Verify DLL was loaded
        mock_cdll.assert_called()
        assert manager.dll == mock_dll

    @patch('os.path.exists')
    def test_init_fails_when_dll_not_found(self, mock_path_exists):
        """Test DLL manager fails when DLL file not found."""
        mock_path_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            DLLManager()

    @patch('os.path.exists')
    @patch('ctypes.CDLL')
    def test_client_property_creates_client(self, mock_cdll, mock_path_exists):
        """Test client property creates and returns client."""
        mock_path_exists.return_value = True
        mock_dll = Mock()
        mock_cdll.return_value = mock_dll
        
        mock_client_instance = Mock()
        mock_dll.CreateClient.return_value = mock_client_instance
        
        manager = DLLManager()
        client = manager.client
        
        mock_dll.CreateClient.assert_called_once()
        assert client == mock_client_instance

    @patch('os.path.exists')
    @patch('ctypes.CDLL')
    def test_trade_property_creates_trade(self, mock_cdll, mock_path_exists):
        """Test trade property creates and returns trade."""
        mock_path_exists.return_value = True
        mock_dll = Mock()
        mock_cdll.return_value = mock_dll
        
        mock_trade_instance = Mock()
        mock_dll.CreateTrade.return_value = mock_trade_instance
        
        manager = DLLManager()
        trade = manager.trade
        
        mock_dll.CreateTrade.assert_called_once()
        assert trade == mock_trade_instance

    @patch('os.path.exists')
    @patch('ctypes.CDLL')
    def test_decimal_property_creates_decimal(self, mock_cdll, mock_path_exists):
        """Test decimal property creates and returns decimal."""
        mock_path_exists.return_value = True
        mock_dll = Mock()
        mock_cdll.return_value = mock_dll
        
        mock_decimal_instance = Mock()
        mock_dll.CreateDecimal.return_value = mock_decimal_instance
        
        manager = DLLManager()
        decimal = manager.decimal
        
        mock_dll.CreateDecimal.assert_called_once()
        assert decimal == mock_decimal_instance

    @patch('os.path.exists')
    @patch('ctypes.CDLL')
    def test_properties_are_cached(self, mock_cdll, mock_path_exists):
        """Test that properties are cached after first access."""
        mock_path_exists.return_value = True
        mock_dll = Mock()
        mock_cdll.return_value = mock_dll
        
        mock_client = Mock()
        mock_trade = Mock()
        mock_decimal = Mock()
        
        mock_dll.CreateClient.return_value = mock_client
        mock_dll.CreateTrade.return_value = mock_trade
        mock_dll.CreateDecimal.return_value = mock_decimal
        
        manager = DLLManager()
        
        # Access properties multiple times
        client1 = manager.client
        client2 = manager.client
        trade1 = manager.trade
        trade2 = manager.trade
        decimal1 = manager.decimal
        decimal2 = manager.decimal
        
        # Verify each DLL function was called only once
        mock_dll.CreateClient.assert_called_once()
        mock_dll.CreateTrade.assert_called_once()
        mock_dll.CreateDecimal.assert_called_once()
        
        # Verify same instances are returned
        assert client1 == client2
        assert trade1 == trade2
        assert decimal1 == decimal2

    @patch('os.path.exists')
    @patch('ctypes.CDLL')
    def test_dll_loading_exception_handling(self, mock_cdll, mock_path_exists):
        """Test DLL loading exception handling."""
        mock_path_exists.return_value = True
        mock_cdll.side_effect = OSError("DLL load failed")
        
        with pytest.raises(OSError, match="DLL load failed"):
            DLLManager()

    @patch('os.path.exists')
    @patch('ctypes.CDLL')
    def test_dll_function_call_exception_handling(self, mock_cdll, mock_path_exists):
        """Test DLL function call exception handling."""
        mock_path_exists.return_value = True
        mock_dll = Mock()
        mock_cdll.return_value = mock_dll
        
        # Mock DLL function to raise exception
        mock_dll.CreateClient.side_effect = Exception("Client creation failed")
        
        manager = DLLManager()
        
        with pytest.raises(Exception, match="Client creation failed"):
            _ = manager.client

    @patch('os.path.exists')
    @patch('ctypes.CDLL')
    def test_dll_path_resolution(self, mock_cdll, mock_path_exists):
        """Test DLL path resolution logic."""
        mock_path_exists.return_value = True
        mock_dll = Mock()
        mock_cdll.return_value = mock_dll
        
        # Mock DLL functions
        mock_dll.CreateClient = Mock()
        mock_dll.CreateTrade = Mock() 
        mock_dll.CreateDecimal = Mock()
        
        manager = DLLManager()
        
        # Verify path checking was called
        mock_path_exists.assert_called()
        
        # Verify DLL loading was attempted
        mock_cdll.assert_called()

    @patch('os.path.exists')
    @patch('ctypes.CDLL')
    def test_manager_handles_missing_dll_functions(self, mock_cdll, mock_path_exists):
        """Test manager handles missing DLL functions gracefully."""
        mock_path_exists.return_value = True
        mock_dll = Mock()
        mock_cdll.return_value = mock_dll
        
        # Remove some DLL functions to simulate incomplete DLL
        del mock_dll.CreateClient
        
        manager = DLLManager()
        
        # Accessing missing function should raise AttributeError
        with pytest.raises(AttributeError):
            _ = manager.client