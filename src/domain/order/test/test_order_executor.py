# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name # for pytest fixtures
# pylint: disable=too-many-arguments

from unittest.mock import MagicMock, call  # Import call for checking logger calls
from typing import TYPE_CHECKING
import pytest

# Imports for types being tested/mocked
from src.domain.order.order_executor import OrderExecutor
from src.infrastructure.messaging import ZmqPuller, serialize
from src.infrastructure.events.trading_signal import TradingSignal
from src.interactor.use_cases.send_market_order import SendMarketOrderUseCase
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.domain.value_objects import OrderOperation, OrderTypeEnum, OpenClose, DayTrade, TimeInForce
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto

# Conditional imports for type checking
if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

# --- Fixtures ---


@pytest.fixture
def mock_zmq_puller(mocker: "MockerFixture") -> MagicMock:
    """Fixture for a mocked ZmqPuller."""
    return mocker.MagicMock(spec=ZmqPuller)


@pytest.fixture
def mock_send_order_use_case(mocker: "MockerFixture") -> MagicMock:
    """Fixture for a mocked SendMarketOrderUseCase."""
    return mocker.MagicMock(spec=SendMarketOrderUseCase)


@pytest.fixture
def mock_session_repository(mocker: "MockerFixture") -> MagicMock:
    """Fixture for a mocked SessionRepositoryInterface."""
    repo = mocker.MagicMock(spec=SessionRepositoryInterface)
    repo.get_order_account.return_value = "TEST_ACCOUNT_123"  # Default successful return
    return repo


@pytest.fixture
def mock_logger(mocker: "MockerFixture") -> MagicMock:
    """Fixture for a mocked LoggerInterface."""
    return mocker.MagicMock(spec=LoggerInterface)


@pytest.fixture
def mock_deserialize(mocker: "MockerFixture") -> MagicMock:
    """Fixture for mocking the deserialize function."""
    return mocker.patch("src.domain.order.order_executor.deserialize")


@pytest.fixture
def order_executor(
    mock_zmq_puller, mock_send_order_use_case, mock_session_repository, mock_logger
) -> OrderExecutor:
    """Fixture to create an OrderExecutor instance with mocked dependencies."""
    return OrderExecutor(
        signal_puller=mock_zmq_puller,
        send_order_use_case=mock_send_order_use_case,
        session_repository=mock_session_repository,
        logger=mock_logger,
        default_quantity=1,
    )


# --- Test Cases ---


def test_process_received_signal_success(
    order_executor: OrderExecutor,
    mock_zmq_puller,
    mock_deserialize,
    mock_send_order_use_case,
    mock_session_repository,
    mock_logger,
):
    """Test processing a valid signal successfully."""
    # Arrange
    commodity_id = "TXF12"
    operation = OrderOperation.BUY
    signal_time = "2023-10-27T10:00:00Z"
    test_signal = TradingSignal(operation=operation, commodity_id=commodity_id, when=signal_time)
    serialized_signal = serialize(
        test_signal
    )  # Use actual serialize if available/simple, else just bytes

    mock_zmq_puller.receive.return_value = serialized_signal
    mock_deserialize.return_value = test_signal
    mock_send_order_use_case.execute.return_value = {"status": "success", "order_id": "order_555"}
    order_account = mock_session_repository.get_order_account.return_value

    # Act
    result = order_executor.process_received_signal()

    # Assert
    assert result is True
    mock_zmq_puller.receive.assert_called_once_with(non_blocking=True)
    mock_deserialize.assert_called_once_with(serialized_signal)
    mock_logger.log_info.assert_any_call(
        f"Received trading signal via ZMQ: {operation.name} {commodity_id} at {signal_time}"
    )
    mock_session_repository.get_order_account.assert_called_once()

    expected_dto = SendMarketOrderInputDto(
        order_account=order_account,
        item_code=commodity_id,
        side=operation,
        order_type=OrderTypeEnum.Market,
        price=0,
        quantity=order_executor.default_quantity,
        open_close=OpenClose.AUTO,
        note=f"Auto order from ZMQ signal at {signal_time}",
        day_trade=DayTrade.No,
        time_in_force=TimeInForce.IOC,
    )
    # Use assert_called_once_with, comparing the DTOs (requires DTOs to have __eq__)
    mock_send_order_use_case.execute.assert_called_once_with(expected_dto)
    mock_logger.log_info.assert_any_call(
        f"Order sent successfully via ZMQ signal. Result: {mock_send_order_use_case.execute.return_value}"
    )
    mock_logger.log_error.assert_not_called()
    mock_logger.log_warning.assert_not_called()


def test_process_received_signal_no_message(
    order_executor: OrderExecutor, mock_zmq_puller, mock_deserialize
):
    """Test behavior when no message is received from the puller."""
    # Arrange
    mock_zmq_puller.receive.return_value = None

    # Act
    result = order_executor.process_received_signal()

    # Assert
    assert result is False
    mock_zmq_puller.receive.assert_called_once_with(non_blocking=True)
    mock_deserialize.assert_not_called()


def test_process_received_signal_deserialization_error(
    order_executor: OrderExecutor, mock_zmq_puller, mock_deserialize, mock_logger
):
    """Test behavior when deserialization fails."""
    # Arrange
    serialized_garbage = b"invalid data"
    mock_zmq_puller.receive.return_value = serialized_garbage
    deserialization_exception = Exception("Bad format!")
    mock_deserialize.side_effect = deserialization_exception

    # Act
    result = order_executor.process_received_signal()

    # Assert
    assert result is True  # Still returns True as a message was consumed
    mock_zmq_puller.receive.assert_called_once_with(non_blocking=True)
    mock_deserialize.assert_called_once_with(serialized_garbage)
    mock_logger.log_error.assert_called_once_with(
        f"Failed to deserialize or process received ZMQ message: {deserialization_exception}"
    )


def test_process_received_signal_wrong_message_type(
    order_executor: OrderExecutor, mock_zmq_puller, mock_deserialize, mock_logger
):
    """Test behavior when the deserialized message is not a TradingSignal."""
    # Arrange
    serialized_data = b"some data"
    wrong_object = {"data": "not a signal"}  # Example of a wrong type
    mock_zmq_puller.receive.return_value = serialized_data
    mock_deserialize.return_value = wrong_object

    # Act
    result = order_executor.process_received_signal()

    # Assert
    assert result is True  # Still returns True as a message was consumed
    mock_zmq_puller.receive.assert_called_once_with(non_blocking=True)
    mock_deserialize.assert_called_once_with(serialized_data)
    mock_logger.log_warning.assert_called_once_with(
        f"Received non-TradingSignal message: {type(wrong_object)}"
    )
    mock_logger.log_error.assert_not_called()


def test_process_received_signal_no_order_account(
    order_executor: OrderExecutor,
    mock_zmq_puller,
    mock_deserialize,
    mock_session_repository,
    mock_logger,
    mock_send_order_use_case,
):
    """Test behavior when session repository doesn't return an order account."""
    # Arrange
    test_signal = TradingSignal(
        operation=OrderOperation.SELL, commodity_id="MXF01", when="2023-10-27T10:05:00Z"
    )
    serialized_signal = serialize(test_signal)

    mock_zmq_puller.receive.return_value = serialized_signal
    mock_deserialize.return_value = test_signal
    mock_session_repository.get_order_account.return_value = None  # Simulate no account found

    # Act
    result = order_executor.process_received_signal()

    # Assert
    assert result is True  # Signal processed, but failed
    mock_zmq_puller.receive.assert_called_once_with(non_blocking=True)
    mock_deserialize.assert_called_once_with(serialized_signal)
    mock_logger.log_info.assert_any_call(
        f"Received trading signal via ZMQ: {test_signal.operation.name} {test_signal.commodity_id} at {test_signal.when}"
    )
    mock_session_repository.get_order_account.assert_called_once()
    mock_logger.log_error.assert_called_once_with("Cannot execute order: No order account selected")
    mock_send_order_use_case.execute.assert_not_called()  # Order should not be sent


def test_process_received_signal_order_execution_fails(
    order_executor: OrderExecutor,
    mock_zmq_puller,
    mock_deserialize,
    mock_send_order_use_case,
    mock_session_repository,
    mock_logger,
):
    """Test behavior when the send_order_use_case execute method raises an exception."""
    # Arrange
    test_signal = TradingSignal(
        operation=OrderOperation.BUY, commodity_id="TXF12", when="2023-10-27T10:10:00Z"
    )
    serialized_signal = serialize(test_signal)

    mock_zmq_puller.receive.return_value = serialized_signal
    mock_deserialize.return_value = test_signal
    execution_exception = Exception("Exchange rejected order!")
    mock_send_order_use_case.execute.side_effect = execution_exception
    # mock_session_repository.get_order_account is already mocked by fixture to return an account

    # Act
    result = order_executor.process_received_signal()

    # Assert
    assert result is True  # Signal processed, but failed
    mock_zmq_puller.receive.assert_called_once_with(non_blocking=True)
    mock_deserialize.assert_called_once_with(serialized_signal)
    mock_session_repository.get_order_account.assert_called_once()
    mock_send_order_use_case.execute.assert_called_once()  # Check execute was called (even if it failed)
    mock_logger.log_error.assert_called_once_with(
        f"Order execution failed for ZMQ signal: {execution_exception}"
    )
    mock_logger.log_info.assert_any_call(
        f"Received trading signal via ZMQ: {test_signal.operation.name} {test_signal.commodity_id} at {test_signal.when}"
    )
    # Ensure success message wasn't logged
    assert (
        call(
            f"Order sent successfully via ZMQ signal. Result: {mock_send_order_use_case.execute.return_value}"
        )
        not in mock_logger.log_info.call_args_list
    )


# Test for the close method (optional, as it's currently empty)
def test_close_method(order_executor: OrderExecutor, mock_logger):
    """Test the close method (currently just logs)."""
    # Arrange
    # No specific arrangement needed

    # Act
    order_executor.close()

    # Assert
    mock_logger.log_info.assert_called_once_with("Closing OrderExecutor resources (ZMQ puller).")
    # If puller.close() were called, add: mock_zmq_puller.close.assert_called_once()
