import pytest
import datetime

from src.infrastructure.messaging.serializer import serialize, deserialize
from src.infrastructure.events.tick import Tick, TickEvent
from src.infrastructure.events.trading_signal import TradingSignal
from src.domain.value_objects import OrderOperation


def test_serialize_deserialize_enum():
    op = OrderOperation.BUY
    data = serialize(op)
    result = deserialize(data)
    assert isinstance(result, OrderOperation)
    assert result is op


def test_serialize_deserialize_datetime():
    dt = datetime.datetime(2021, 5, 4, 12, 30, 45, 123456)
    data = serialize(dt)
    result = deserialize(data)
    assert isinstance(result, datetime.datetime)
    # Compare ISO format to avoid timezone differences
    assert result.isoformat().startswith('2021-05-04T12:30:45')


def test_serialize_deserialize_tick():
    tick = Tick(commodity_id='C1', match_price=99.9)
    data = serialize(tick)
    result = deserialize(data)
    assert isinstance(result, Tick)
    assert result.commodity_id == 'C1'
    assert result.match_price == 99.9


def test_serialize_deserialize_tick_event():
    dt = datetime.datetime.utcnow()
    tick = Tick('C2', 50.5)
    ev = TickEvent(dt, tick)
    data = serialize(ev)
    result = deserialize(data)
    assert isinstance(result, TickEvent)
    assert result.when == dt
    assert isinstance(result.tick, Tick)
    assert result.tick.match_price == 50.5


def test_serialize_deserialize_trading_signal():
    dt = datetime.datetime.utcnow()
    sig = TradingSignal(dt, OrderOperation.SELL, 'X9')
    data = serialize(sig)
    result = deserialize(data)
    assert isinstance(result, TradingSignal)
    assert result.when == dt
    assert result.operation == OrderOperation.SELL
    assert result.commodity_id == 'X9'


def test_serialize_complex_structure():
    # Nested list containing different serializable types
    dt = datetime.datetime.utcnow()
    tick = Tick('C3', 77.7)
    sig = TradingSignal(dt, OrderOperation.BUY, 'Y1')
    payload = {'time': dt, 'events': [tick, sig, OrderOperation.SELL]}
    data = serialize(payload)
    result = deserialize(data)
    assert isinstance(result, dict)
    assert result['time'].isoformat().startswith(dt.isoformat()[:19])
    ev_list = result['events']
    assert isinstance(ev_list, list) and len(ev_list) == 3
    assert isinstance(ev_list[0], Tick)
    assert isinstance(ev_list[1], TradingSignal)
    assert ev_list[2] == OrderOperation.SELL
