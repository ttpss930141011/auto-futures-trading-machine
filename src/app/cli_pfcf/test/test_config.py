import os
import sys
import pytest

from src.app.cli_pfcf.config import Config


def test_config_properties(monkeypatch):
    # Setup environment variables
    monkeypatch.setenv('DEALER_TEST_URL', 'test_url')
    monkeypatch.setenv('DEALER_PROD_URL', 'prod_url')
    # Create config - no longer needs exchange API
    cfg = Config()
    # Test URL properties
    assert cfg.EXCHANGE_TEST_URL == 'test_url'
    assert cfg.EXCHANGE_PROD_URL == 'prod_url'
    # Test ZMQ address properties
    host = cfg.ZMQ_HOST
    tz = cfg.ZMQ_TICK_PORT
    sz = cfg.ZMQ_SIGNAL_PORT
    assert cfg.ZMQ_TICK_PUB_ADDRESS == f"tcp://{host}:{tz}"
    assert cfg.ZMQ_SIGNAL_PULL_ADDRESS == f"tcp://{host}:{sz}"
    assert cfg.ZMQ_TICK_SUB_CONNECT_ADDRESS == f"tcp://localhost:{tz}"
    assert cfg.ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS == f"tcp://localhost:{sz}"


def test_config_with_valid_env_vars(monkeypatch):
    """Test config creation with valid environment variables."""
    # Ensure URLs exist
    monkeypatch.setenv('DEALER_TEST_URL', 'test')
    monkeypatch.setenv('DEALER_PROD_URL', 'prod')
    # Config should initialize successfully
    cfg = Config()
    assert cfg.EXCHANGE_TEST_URL == 'test'
    assert cfg.EXCHANGE_PROD_URL == 'prod'


def test_config_missing_env_vars(monkeypatch):
    """Test config fails when required environment variables are missing."""
    # Remove URLs
    monkeypatch.delenv('DEALER_TEST_URL', raising=False)
    monkeypatch.delenv('DEALER_PROD_URL', raising=False)
    # Missing test URL first
    with pytest.raises(SystemExit):
        Config()
    # Set test URL only
    monkeypatch.setenv('DEALER_TEST_URL', 'test')
    with pytest.raises(SystemExit):
        Config()
