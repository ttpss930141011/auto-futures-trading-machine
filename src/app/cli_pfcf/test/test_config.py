import os
import sys
import pytest

from src.app.cli_pfcf.config import Config


class DummyApi:
    """Dummy exchange API with required attributes."""
    def __init__(self):
        self.client = object()
        self.trade = object()
        self.decimal = object()


def test_config_properties(monkeypatch):
    # Setup environment variables
    monkeypatch.setenv('DEALER_TEST_URL', 'test_url')
    monkeypatch.setenv('DEALER_PROD_URL', 'prod_url')
    # Create config with dummy api
    api = DummyApi()
    cfg = Config(api)
    # Test that exchange attributes are set
    assert cfg.EXCHANGE_CLIENT is api.client
    assert cfg.EXCHANGE_TRADE is api.trade
    assert cfg.EXCHANGE_DECIMAL is api.decimal
    # Test ZMQ address properties
    host = cfg.ZMQ_HOST
    tz = cfg.ZMQ_TICK_PORT
    sz = cfg.ZMQ_SIGNAL_PORT
    assert cfg.ZMQ_TICK_PUB_ADDRESS == f"tcp://{host}:{tz}"
    assert cfg.ZMQ_SIGNAL_PULL_ADDRESS == f"tcp://{host}:{sz}"
    assert cfg.ZMQ_TICK_SUB_CONNECT_ADDRESS == f"tcp://localhost:{tz}"
    assert cfg.ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS == f"tcp://localhost:{sz}"


@pytest.mark.parametrize('missing_attr', ['client', 'trade'])
def test_config_missing_api_attr(monkeypatch, missing_attr):
    # Ensure URLs exist
    monkeypatch.setenv('DEALER_TEST_URL', 'test')
    monkeypatch.setenv('DEALER_PROD_URL', 'prod')
    # Create dummy api and remove attribute
    api = DummyApi()
    delattr(api, missing_attr)
    # Expect SystemExit on missing api attributes
    with pytest.raises(SystemExit):
        Config(api)


def test_config_missing_env_vars(monkeypatch):
    # Remove URLs
    monkeypatch.delenv('DEALER_TEST_URL', raising=False)
    monkeypatch.delenv('DEALER_PROD_URL', raising=False)
    api = DummyApi()
    # Missing test URL first
    with pytest.raises(SystemExit):
        Config(api)
    # Set test URL only
    monkeypatch.setenv('DEALER_TEST_URL', 'test')
    with pytest.raises(SystemExit):
        Config(api)