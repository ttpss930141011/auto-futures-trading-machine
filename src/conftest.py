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
def fixture_register_item():
    """Fixture with Window example"""
    return {
        "account": "12345678900",
        "item_code": "1234567890",
    }


@pytest.fixture
def fixture_tick_data_trade():
    """Fixture with Window example"""
    return {'commodity_id': 'TXFD4',
            'info_time': '040943817000',
            'match_time': '040943766000',
            'match_price': '20247',
            'match_buy_cnt': '29894',
            'match_sell_cnt': '27403',
            'match_quantity': '1',
            'match_total_qty': '45773'
            }


@pytest.fixture
def session_manager():
    session_timeout = 1  # 1 second
    return SessionManager(session_timeout)
