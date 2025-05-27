import pytest
import uuid

from src.domain.entities.condition import Condition
from src.domain.value_objects import OrderOperation


def test_condition_buy_computes_prices():
    cid = uuid.uuid4()
    cond = Condition(
        condition_id=cid,
        action=OrderOperation.BUY,
        trigger_price=100,
        quantity=5,
        turning_point=10,
        take_profit_point=20,
        stop_loss_point=15,
    )
    assert cond.order_price == 110
    assert cond.take_profit_price == 130
    assert cond.stop_loss_price == 95
    assert not cond.is_trigger
    assert not cond.is_ordered
    # repr and str
    assert repr(cond) == f'<Condition {cid}>'
    assert str(cond) == f'<Condition {cid}>'


def test_condition_sell_computes_prices():
    cid = uuid.uuid4()
    cond = Condition(
        condition_id=cid,
        action=OrderOperation.SELL,
        trigger_price=200,
        quantity=2,
        turning_point=5,
        take_profit_point=25,
        stop_loss_point=10,
    )
    assert cond.order_price == 195
    assert cond.take_profit_price == 170
    assert cond.stop_loss_price == 205


@pytest.mark.parametrize("field", [
    'condition_id', 'action', 'trigger_price', 'quantity'
])
def test_condition_missing_required(field):
    params = {
        'condition_id': uuid.uuid4(),
        'action': OrderOperation.BUY,
        'trigger_price': 100,
        'quantity': 1,
    }
    params[field] = None
    with pytest.raises(ValueError):
        Condition(**params)


def test_condition_invalid_action():
    params = {
        'condition_id': uuid.uuid4(),
        'action': 'INVALID',
        'trigger_price': 100,
        'quantity': 1,
    }
    with pytest.raises(ValueError):
        Condition(**params)


def test_from_dict_filters_extra_and_to_dict():
    cid2 = uuid.uuid4()
    data = {
        'condition_id': cid2,
        'action': OrderOperation.SELL,
        'trigger_price': 50,
        'quantity': 3,
        'turning_point': 7,
        'take_profit_point': 14,
        'stop_loss_point': 8,
        'is_following': True,
        'extra_field': 'ignore',
    }
    cond = Condition.from_dict(data)
    # extra_field is ignored
    assert not hasattr(cond, 'extra_field')
    # check computed
    assert cond.order_price == 43
    # to_dict includes all fields
    d = cond.to_dict()
    assert d['condition_id'] == cid2
    assert d['action'] == data['action']
    assert d['is_following'] is True