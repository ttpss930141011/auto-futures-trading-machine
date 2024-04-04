import pytest

from src.domain.value_objects import OrderOperation, OrderTypeEnum, TimeInForce, OpenClose, DayTrade
from src.infrastructure.repositories.session_in_memory_repository import SessionInMemoryRepository


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
def fixture_select_order_account():
    """Fixture with select_order_account example"""
    return {
        "index_input": "1",
        "index": 0,
        "order_account": "12345678900",
    }


@pytest.fixture
def fixture_create_condition():
    """Fixture with create_condition example"""
    return {
        "action": OrderOperation.BUY,
        "trigger_price": 100,
        "turning_point": 10,
        "quantity": 10,
        "take_profit_point": 10,
        "stop_loss_point": 10,
        "is_following": True
    }


@pytest.fixture
def fixture_send_market_order():
    """Fixture with send_market_order example"""
    return {
        "order_account": "12345678900",
        "item_code": "1234567890",
        "side": OrderOperation.BUY,
        "order_type": OrderTypeEnum.Market,
        "price": 100,
        "quantity": 10,
        "time_in_force": TimeInForce.IOC,
        "open_close": OpenClose.AUTO,
        "day_trade": DayTrade.No,
        "note": "note"
    }


@pytest.fixture
def session_manager():
    session_timeout = 1  # 1 second
    return SessionInMemoryRepository(session_timeout)
