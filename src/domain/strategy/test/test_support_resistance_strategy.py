# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name # for pytest fixtures
# pylint: disable=too-many-arguments
# pylint: disable=protected-access # To test private methods if needed or access members

import pytest
from typing import TYPE_CHECKING, Dict, Any, Optional
from unittest.mock import MagicMock, call
import datetime

from src.domain.strategy.test.helper.create_condition import create_condition
from src.domain.strategy.test.helper.create_tick_event import create_tick_event
from src.domain.strategy.test.helper.set_condition_state import set_condition_state

# Imports for types being tested/mocked
from src.domain.strategy.support_resistance_strategy import SupportResistanceStrategy
from src.infrastructure.events.tick import TickEvent, Tick
from src.infrastructure.messaging import ZmqPusher, serialize
from src.infrastructure.events.trading_signal import TradingSignal
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.domain.entities.condition import Condition
from src.domain.value_objects import OrderOperation

# Conditional imports for type checking
if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

# --- Helper Functions/Fixtures ---


@pytest.fixture
def mock_condition_repo(mocker: "MockerFixture") -> MagicMock:
    """Fixture for a mocked ConditionRepositoryInterface."""
    repo = mocker.MagicMock(spec=ConditionRepositoryInterface)
    repo.get_all.return_value = {}  # Default to no conditions
    repo.conditions_storage = {}  # Simulate storage for get/update/delete

    def _get_all():
        return repo.conditions_storage

    def _update(condition: Condition):
        if condition.condition_id in repo.conditions_storage:
            repo.conditions_storage[condition.condition_id] = condition
        else:
            raise KeyError(f"Condition {condition.condition_id} not found for update")

    def _delete(condition_id: str):
        if condition_id in repo.conditions_storage:
            del repo.conditions_storage[condition_id]
        # No error if already deleted

    def _get_by_id(condition_id: str) -> Optional[Condition]:
        return repo.conditions_storage.get(condition_id)

    repo.get_all.side_effect = _get_all
    repo.update.side_effect = _update
    repo.delete.side_effect = _delete
    repo.get_by_id = _get_by_id

    return repo


@pytest.fixture
def mock_signal_pusher(mocker: "MockerFixture") -> MagicMock:
    """Fixture for a mocked ZmqPusher."""
    return mocker.MagicMock(spec=ZmqPusher)


@pytest.fixture
def mock_logger(mocker: "MockerFixture") -> MagicMock:
    """Fixture for a mocked LoggerInterface."""
    logger = mocker.MagicMock(spec=LoggerInterface)
    # Ensure all expected log methods exist
    logger.log_info = MagicMock()
    logger.log_warning = MagicMock()
    logger.log_error = MagicMock()
    return logger


@pytest.fixture
def mock_serialize(mocker: "MockerFixture") -> MagicMock:
    """Fixture for mocking the infrastructure serialize function."""
    # Mock the serialize function used within the strategy module
    return mocker.patch("src.domain.strategy.support_resistance_strategy.serialize")


@pytest.fixture
def strategy(mock_condition_repo, mock_signal_pusher, mock_logger) -> SupportResistanceStrategy:
    """Fixture to create a Strategy instance with mocked dependencies."""
    return SupportResistanceStrategy(
        condition_repository=mock_condition_repo,
        signal_pusher=mock_signal_pusher,
        logger=mock_logger,
    )


# --- Test Cases ---


def test_process_tick_no_conditions(
    strategy: SupportResistanceStrategy, mock_condition_repo, mock_signal_pusher
):
    """Test processing a tick when there are no conditions."""
    # Arrange
    mock_condition_repo.get_all.return_value = {}  # Explicitly set no conditions
    tick_event = create_tick_event(18000)

    # Act
    strategy.process_tick_event(tick_event)

    # Assert
    mock_condition_repo.get_all.assert_called_once()
    mock_signal_pusher.send.assert_not_called()
    mock_condition_repo.update.assert_not_called()
    mock_condition_repo.delete.assert_not_called()


def test_buy_condition_trigger(strategy: SupportResistanceStrategy, mock_condition_repo):
    """Test a BUY condition triggers when price drops below support."""
    # Arrange
    condition = create_condition(
        "C1",
        OrderOperation.BUY,
        trigger=18000,
        quantity=1,
        tp_points=100,
        sl_points=50,
        turning_points=50,
    )
    mock_condition_repo.conditions_storage = {"C1": condition}
    tick_event = create_tick_event(17990)  # Price below trigger

    # Act
    strategy.process_tick_event(tick_event)

    # Assert
    updated_condition = mock_condition_repo.get_by_id("C1")
    assert updated_condition.is_trigger is True
    assert updated_condition.is_ordered is False
    assert updated_condition.is_exited is False
    mock_condition_repo.update.assert_called_once_with(updated_condition)


def test_sell_condition_trigger(strategy: SupportResistanceStrategy, mock_condition_repo):
    """Test a SELL condition triggers when price rises above resistance."""
    # Arrange
    condition = create_condition(
        "C1",
        OrderOperation.SELL,
        trigger=18100,
        quantity=1,
        tp_points=100,
        sl_points=50,
        turning_points=50,
    )
    mock_condition_repo.conditions_storage = {"C1": condition}
    tick_event = create_tick_event(18110)  # Price above trigger

    # Act
    strategy.process_tick_event(tick_event)

    # Assert
    updated_condition = mock_condition_repo.get_by_id("C1")
    assert updated_condition.is_trigger is True
    assert updated_condition.is_ordered is False
    assert updated_condition.is_exited is False
    mock_condition_repo.update.assert_called_once_with(updated_condition)


def test_buy_condition_order(
    strategy: SupportResistanceStrategy, mock_condition_repo, mock_signal_pusher, mock_serialize
):
    """Test a triggered BUY condition orders when price rises to order level."""
    # Arrange
    condition = create_condition(
        "C1",
        OrderOperation.BUY,
        trigger=18000,
        quantity=1,
        tp_points=100,
        sl_points=50,
        turning_points=50,
    )
    set_condition_state(condition, is_trigger=True)
    mock_condition_repo.conditions_storage = {"C1": condition}
    tick_event = create_tick_event(
        18055, timestamp=datetime.datetime(2024, 1, 1, 10, 0, 0)
    )  # Price above calculated order_price (18000+50)
    # Keep expected_signal for attribute comparison
    expected_signal_attrs = TradingSignal(
        tick_event.when, OrderOperation.BUY, tick_event.tick.commodity_id
    )
    serialized_signal = b"serialized_buy_signal"
    mock_serialize.return_value = serialized_signal

    # Act
    strategy.process_tick_event(tick_event)

    # Assert
    updated_condition = mock_condition_repo.get_by_id("C1")
    assert updated_condition.is_trigger is True
    assert updated_condition.is_ordered is True  # Check state change
    assert updated_condition.is_exited is False

    # Capture the argument passed to serialize and check attributes
    mock_serialize.assert_called_once()
    actual_signal_arg = mock_serialize.call_args[0][0]  # Get the first positional arg
    assert isinstance(actual_signal_arg, TradingSignal)
    assert actual_signal_arg.when == expected_signal_attrs.when
    assert actual_signal_arg.operation == expected_signal_attrs.operation
    assert actual_signal_arg.commodity_id == expected_signal_attrs.commodity_id

    mock_signal_pusher.send.assert_called_once_with(serialized_signal)
    mock_condition_repo.update.assert_called_once_with(updated_condition)


def test_sell_condition_order(
    strategy: SupportResistanceStrategy, mock_condition_repo, mock_signal_pusher, mock_serialize
):
    """Test a triggered SELL condition orders when price drops to order level."""
    # Arrange
    condition = create_condition(
        "C1",
        OrderOperation.SELL,
        trigger=18100,
        quantity=1,
        tp_points=100,
        sl_points=50,
        turning_points=50,
    )
    set_condition_state(condition, is_trigger=True)
    mock_condition_repo.conditions_storage = {"C1": condition}
    tick_event = create_tick_event(
        18045, timestamp=datetime.datetime(2024, 1, 1, 10, 5, 0)
    )  # Price below calculated order_price (18100-50)
    # Keep expected_signal for attribute comparison
    expected_signal_attrs = TradingSignal(
        tick_event.when, OrderOperation.SELL, tick_event.tick.commodity_id
    )
    serialized_signal = b"serialized_sell_signal"
    mock_serialize.return_value = serialized_signal

    # Act
    strategy.process_tick_event(tick_event)

    # Assert
    updated_condition = mock_condition_repo.get_by_id("C1")
    assert updated_condition.is_trigger is True
    assert updated_condition.is_ordered is True  # Check state change
    assert updated_condition.is_exited is False

    # Capture the argument passed to serialize and check attributes
    mock_serialize.assert_called_once()
    actual_signal_arg = mock_serialize.call_args[0][0]  # Get the first positional arg
    assert isinstance(actual_signal_arg, TradingSignal)
    assert actual_signal_arg.when == expected_signal_attrs.when
    assert actual_signal_arg.operation == expected_signal_attrs.operation
    assert actual_signal_arg.commodity_id == expected_signal_attrs.commodity_id

    mock_signal_pusher.send.assert_called_once_with(serialized_signal)
    mock_condition_repo.update.assert_called_once_with(updated_condition)


# --- Exit Condition Tests ---


@pytest.mark.parametrize(
    "entry_action, exit_price, expected_exit_action, exit_reason",
    [
        (
            OrderOperation.BUY,
            18105,
            OrderOperation.SELL,
            "Take profit",
        ),  # Buy hits TP (order=18050, tp=18100)
        (
            OrderOperation.BUY,
            17945,
            OrderOperation.SELL,
            "Stop loss",
        ),  # Buy hits SL (order=18050, sl=17950)
        (
            OrderOperation.SELL,
            17995,
            OrderOperation.BUY,
            "Take profit",
        ),  # Sell hits TP (order=18050, tp=18000)
        (
            OrderOperation.SELL,
            18155,
            OrderOperation.BUY,
            "Stop loss",
        ),  # Sell hits SL (order=18050, sl=18150)
    ],
)
def test_exit_conditions(
    strategy: SupportResistanceStrategy,
    mock_condition_repo,
    mock_signal_pusher,
    mock_serialize,
    mock_logger,
    entry_action: OrderOperation,
    exit_price: int,
    expected_exit_action: OrderOperation,
    exit_reason: str,
):
    """Test exit conditions (Take Profit and Stop Loss) for BUY and SELL."""
    # Arrange
    if entry_action == OrderOperation.BUY:
        condition = create_condition(
            "C1",
            entry_action,
            trigger=18000,
            quantity=1,
            tp_points=50,
            sl_points=100,
            turning_points=50,
        )
        # Calculated: order=18050, tp=18100, sl=17950
    else:  # SELL
        condition = create_condition(
            "C1",
            entry_action,
            trigger=18100,
            quantity=1,
            tp_points=50,
            sl_points=100,
            turning_points=50,
        )
        # Calculated: order=18050, tp=18000, sl=18150

    set_condition_state(condition, is_trigger=True, is_ordered=True)  # Set state after creation
    mock_condition_repo.conditions_storage = {"C1": condition}
    tick_event = create_tick_event(exit_price, timestamp=datetime.datetime(2024, 1, 1, 10, 10, 0))
    # Keep expected_signal for attribute comparison
    expected_signal_attrs = TradingSignal(
        tick_event.when, expected_exit_action, tick_event.tick.commodity_id
    )
    serialized_signal = b"serialized_exit_signal"
    mock_serialize.return_value = serialized_signal

    # Act
    strategy.process_tick_event(tick_event)

    # Assert
    # Condition should be deleted
    assert mock_condition_repo.get_by_id("C1") is None
    mock_logger.log_info.assert_any_call(f"Condition C1 exiting: {exit_reason}")

    # mock_serialize.assert_called_once_with(expected_signal) # <-- Replace this
    # Capture the argument passed to serialize and check attributes
    mock_serialize.assert_called_once()
    actual_signal_arg = mock_serialize.call_args[0][0]  # Get the first positional arg
    assert isinstance(actual_signal_arg, TradingSignal)
    assert actual_signal_arg.when == expected_signal_attrs.when
    assert actual_signal_arg.operation == expected_signal_attrs.operation
    assert actual_signal_arg.commodity_id == expected_signal_attrs.commodity_id

    mock_signal_pusher.send.assert_called_once_with(serialized_signal)
    mock_condition_repo.delete.assert_called_once_with("C1")
    mock_condition_repo.update.assert_not_called()  # Should not update after deletion


# --- Trailing Condition Tests ---


def test_trailing_buy_update(strategy: SupportResistanceStrategy, mock_condition_repo):
    """Test trailing BUY condition updates trigger/order prices as price drops."""
    # Arrange
    initial_trigger = 18000
    turning_point = 50
    condition = create_condition(
        "C1",
        OrderOperation.BUY,
        trigger=initial_trigger,
        quantity=1,
        tp_points=100,
        sl_points=50,
        turning_points=turning_point,
        is_following=True,
    )
    # Calculated initial order = 18050
    mock_condition_repo.conditions_storage = {"C1": condition}
    new_low_price = 17980  # Price drops below initial trigger
    tick_event = create_tick_event(new_low_price)

    # Act
    strategy.process_tick_event(tick_event)

    # Assert
    updated_condition = mock_condition_repo.get_by_id("C1")
    assert updated_condition.is_trigger is True
    assert updated_condition.trigger_price == new_low_price
    assert updated_condition.order_price == new_low_price + turning_point
    mock_condition_repo.update.assert_called_once_with(updated_condition)


def test_trailing_sell_update(strategy: SupportResistanceStrategy, mock_condition_repo):
    """Test trailing SELL condition updates trigger/order prices as price rises."""
    # Arrange
    initial_trigger = 18100
    turning_point = 50
    condition = create_condition(
        "C1",
        OrderOperation.SELL,
        trigger=initial_trigger,
        quantity=1,
        tp_points=100,
        sl_points=50,
        turning_points=turning_point,
        is_following=True,
    )
    # Calculated initial order = 18050
    mock_condition_repo.conditions_storage = {"C1": condition}
    new_high_price = 18120  # Price rises above initial trigger
    tick_event = create_tick_event(new_high_price)

    # Act
    strategy.process_tick_event(tick_event)

    # Assert
    updated_condition = mock_condition_repo.get_by_id("C1")
    assert updated_condition.is_trigger is True
    assert updated_condition.trigger_price == new_high_price
    assert updated_condition.order_price == new_high_price - turning_point
    mock_condition_repo.update.assert_called_once_with(updated_condition)


# --- Error Handling/Edge Cases ---


def test_signal_send_exception(
    strategy: SupportResistanceStrategy,
    mock_condition_repo,
    mock_signal_pusher,
    mock_serialize,
    mock_logger,
):
    """Test handling of exception when sending signal via pusher."""
    # Arrange
    condition = create_condition(
        "C1",
        OrderOperation.BUY,
        trigger=18000,
        quantity=1,
        tp_points=100,
        sl_points=50,
        turning_points=50,
    )
    set_condition_state(condition, is_trigger=True)
    mock_condition_repo.conditions_storage = {"C1": condition}
    tick_event = create_tick_event(18055)  # Price above calculated order_price (18000+50)
    expected_signal = TradingSignal(
        tick_event.when, OrderOperation.BUY, tick_event.tick.commodity_id
    )
    serialized_signal = b"serialized_buy_signal"
    mock_serialize.return_value = serialized_signal
    send_error = Exception("ZMQ Send Failed!")
    mock_signal_pusher.send.side_effect = send_error

    # Act
    strategy.process_tick_event(tick_event)

    # Assert
    updated_condition = mock_condition_repo.get_by_id("C1")
    # Condition should still be marked as ordered because the *intent* was there
    assert updated_condition.is_ordered is True
    mock_logger.log_error.assert_called_once_with(
        f"Failed to send trading signal via ZMQ: {send_error}"
    )
    mock_condition_repo.update.assert_called_once_with(updated_condition)


def test_close_method(strategy: SupportResistanceStrategy, mock_logger):
    """Test the close method logs correctly."""
    # Act
    strategy.close()
    # Assert
    mock_logger.log_info.assert_called_once_with("Closing Strategy resources (ZMQ pusher).")
