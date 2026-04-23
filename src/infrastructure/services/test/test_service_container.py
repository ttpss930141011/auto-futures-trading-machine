"""Integration tests for ServiceContainer attribute contract.

These tests use a real ServiceContainer (not MagicMock) to catch naming
mismatches between callers and the container's actual attributes.
Mock-only tests miss these because MagicMock accepts any attribute.
"""

from unittest.mock import MagicMock

import pytest

from src.infrastructure.services.service_container import ServiceContainer


@pytest.fixture
def real_container():
    """ServiceContainer with mocked dependencies but real attribute lookup."""
    exchange_api = MagicMock()
    exchange_api.client = MagicMock(name="pfcf_client")
    exchange_api.trade = MagicMock(name="pfcf_trade")
    return ServiceContainer(
        logger=MagicMock(),
        config=MagicMock(),
        session_repository=MagicMock(),
        condition_repository=MagicMock(),
        exchange_api=exchange_api,
    )


class TestServiceContainerAttributes:
    """Pin the attribute contract so callers can rely on it."""

    def test_has_exchange_api(self, real_container):
        assert hasattr(real_container, "exchange_api")

    def test_exchange_client_goes_through_exchange_api(self, real_container):
        """Callers must access the PFCF client via exchange_api.client."""
        assert real_container.exchange_api.client is not None

    def test_exchange_trade_goes_through_exchange_api(self, real_container):
        """Callers must access the PFCF trade module via exchange_api.trade."""
        assert real_container.exchange_api.trade is not None

    def test_exposed_public_attrs(self, real_container):
        """Lock the public surface to prevent accidental widening."""
        public_attrs = {a for a in dir(real_container) if not a.startswith("_")}
        assert public_attrs == {
            "logger",
            "config",
            "session_repository",
            "condition_repository",
            "exchange_api",
        }
