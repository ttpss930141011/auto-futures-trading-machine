import pytest

from src.infrastructure.session_manager.session_manager import SessionManager


@pytest.fixture
def fixture_user():
    """Fixture with Window example"""
    return {
        "account": "12345678900",
        "password": "1234567890",  # NOSONAR
        "ip_address": "192.168.1.1",  # NOSONAR
        "client": "client"
    }


@pytest.fixture
def session_manager():
    session_timeout = 1  # 1 second
    return SessionManager(session_timeout)
