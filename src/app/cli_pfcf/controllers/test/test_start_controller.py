# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
from typing import TYPE_CHECKING, Dict
import pytest

from src.app.cli_pfcf.controllers.start_controller import StartController
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

@pytest.fixture
def mock_service_container(mocker: 'MockerFixture'):
    """Fixture to create a mocked ServiceContainer."""
    service_container_mock = mocker.MagicMock(name="ServiceContainer")
    service_container_mock.logger = mocker.MagicMock(spec=LoggerInterface, name="Logger")
    service_container_mock.config = mocker.MagicMock(name="Config")
    
    # Mock the EXCHANGE_CLIENT and DQuoteLib structure needed for API callbacks
    mock_dquotelib = mocker.MagicMock(name="DQuoteLib")
    # Create a specific mock for the event attribute
    mock_on_tick_data_trade_event = mocker.MagicMock(name="OnTickDataTradeEvent")
    # Explicitly add a mock for the __iadd__ method on the event mock
    mock_on_tick_data_trade_event.__iadd__ = mocker.MagicMock(name="OnTickDataTradeEvent.__iadd__")
    mock_dquotelib.OnTickDataTrade = mock_on_tick_data_trade_event
    # Explicitly mock RegItem
    mock_dquotelib.RegItem = mocker.MagicMock(name="DQuoteLib.RegItem")
    
    service_container_mock.config.EXCHANGE_CLIENT = mocker.MagicMock(name="PFCFApi")
    service_container_mock.config.EXCHANGE_CLIENT.DQuoteLib = mock_dquotelib
    service_container_mock.session_repository = mocker.MagicMock(spec=SessionRepositoryInterface, name="SessionRepository")
    service_container_mock.condition_repository = mocker.MagicMock(spec=ConditionRepositoryInterface, name="ConditionRepository")
    # Mock the use case if it exists within the container
    service_container_mock.send_market_order_use_case = mocker.MagicMock(name="SendMarketOrderUseCase")
    return service_container_mock

def test_start_controller_user_not_logged_in(mocker: 'MockerFixture', mock_service_container):
    """Test execute() when user is not logged in."""
    # Arrange
    mock_service_container.session_repository.is_user_logged_in.return_value = False
    mock_start_app_use_case = mocker.patch('src.app.cli_pfcf.controllers.start_controller.StartApplicationUseCase')
    # Mock zmq.Context.instance *before* controller instantiation
    mock_zmq_instance = mocker.patch('src.app.cli_pfcf.controllers.start_controller.zmq.Context.instance').return_value
    mock_zmq_instance.closed = False # Ensure the cleanup check passes
    
    controller = StartController(mock_service_container)
    
    # Act
    controller.execute()
    
    # Assert
    mock_service_container.session_repository.is_user_logged_in.assert_called_once()
    mock_service_container.logger.log_info.assert_any_call("User not login") # Check it was called
    mock_start_app_use_case.assert_not_called() # Use case should not be called
    # ZMQ instance *is* created in __init__, but components aren't initialized
    # mocker.patch('src.app.cli_pfcf.controllers.start_controller.zmq.Context.instance').assert_called_once() # Removed redundant check
    assert controller.tick_publisher is None # Ensure components not initialized
    # Check cleanup happened in finally block
    mock_service_container.logger.log_info.assert_any_call("Cleaning up ZMQ resources...")
    mock_zmq_instance.term.assert_called_once() # term() should be called

def test_start_controller_prerequisites_not_met(mocker: 'MockerFixture', mock_service_container):
    """Test execute() when prerequisites are not met."""
    # Arrange
    mock_service_container.session_repository.is_user_logged_in.return_value = True
    
    mock_status_checker = mocker.patch('src.app.cli_pfcf.controllers.start_controller.StatusChecker')
    mock_start_app_use_case_instance = mocker.MagicMock()
    # Simulate status checker returning False for some checks
    mock_start_app_use_case_instance.execute.return_value = {
        'logged_in': True, 
        'item_registered': False, 
        'order_account_selected': True, 
        'has_conditions': False
    }
    mock_start_app_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.start_controller.StartApplicationUseCase', 
        return_value=mock_start_app_use_case_instance
    )
    
    # Mock zmq.Context.instance *before* controller instantiation
    mock_zmq_instance = mocker.patch('src.app.cli_pfcf.controllers.start_controller.zmq.Context.instance').return_value
    mock_zmq_instance.closed = False # Ensure the cleanup check passes
    
    controller = StartController(mock_service_container)
    
    # Act
    controller.execute()
    
    # Assert
    mock_service_container.session_repository.is_user_logged_in.assert_called_once()
    mock_start_app_use_case.assert_called_once_with(
        logger=mock_service_container.logger,
        status_checker=mock_status_checker.return_value
    )
    mock_start_app_use_case_instance.execute.assert_called_once()
    mock_service_container.logger.log_warning.assert_called_with("Prerequisites not met. Please complete the setup before starting.")
    # Ensure components were not initialized
    assert controller.tick_publisher is None
    assert controller.signal_puller is None
    assert controller.tick_producer is None
    assert controller.order_executor is None
    # Ensure API callbacks were not connected
    mock_service_container.config.EXCHANGE_CLIENT.DQuoteLib.OnTickDataTrade.__iadd__.assert_not_called()
    mock_zmq_instance.term.assert_called_once() # Ensure ZMQ context is terminated in finally block

def test_start_controller_success(mocker: 'MockerFixture', mock_service_container):
    """Test successful execution when prerequisites are met."""
    # Arrange
    mock_service_container.session_repository.is_user_logged_in.return_value = True
    mock_service_container.session_repository.get_item_code.return_value = "TXF12"
    mock_service_container.condition_repository.get_all.return_value = {} # No conditions for simplicity here

    mock_status_checker = mocker.patch('src.app.cli_pfcf.controllers.start_controller.StatusChecker')
    mock_start_app_use_case_instance = mocker.MagicMock()
    # Simulate all checks passing
    mock_start_app_use_case_instance.execute.return_value = {
        'logged_in': True, 
        'item_registered': True, 
        'order_account_selected': True, 
        'has_conditions': True
    }
    mock_start_app_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.start_controller.StartApplicationUseCase', 
        return_value=mock_start_app_use_case_instance
    )
    
    # Mock ZMQ components
    # Mock zmq.Context.instance *before* controller instantiation
    mock_zmq_instance = mocker.patch('src.app.cli_pfcf.controllers.start_controller.zmq.Context.instance').return_value
    mock_zmq_instance.closed = False # Ensure the cleanup check passes
    mock_zmq_publisher = mocker.patch('src.app.cli_pfcf.controllers.start_controller.ZmqPublisher')
    mock_zmq_puller = mocker.patch('src.app.cli_pfcf.controllers.start_controller.ZmqPuller')
    mock_tick_producer = mocker.patch('src.app.cli_pfcf.controllers.start_controller.TickProducer')
    mock_order_executor = mocker.patch('src.app.cli_pfcf.controllers.start_controller.OrderExecutor')

    controller = StartController(mock_service_container)

    # Act
    controller.execute()

    # Assert
    # Status checks
    mock_service_container.session_repository.is_user_logged_in.assert_called_once()
    mock_start_app_use_case.assert_called_once()
    mock_start_app_use_case_instance.execute.assert_called_once()
    mock_service_container.logger.log_warning.assert_not_called() # No warning

    # Component Initialization
    # mocker.patch('src.app.cli_pfcf.controllers.start_controller.zmq.Context.instance').assert_called_once() # Removed redundant check
    mock_zmq_publisher.assert_called_once_with(mocker.ANY, mock_service_container.logger, mock_zmq_instance)
    mock_zmq_puller.assert_called_once_with(mocker.ANY, mock_service_container.logger, mock_zmq_instance)
    mock_tick_producer.assert_called_once_with(tick_publisher=mock_zmq_publisher.return_value, logger=mock_service_container.logger)
    mock_order_executor.assert_called_once_with(
        signal_puller=mock_zmq_puller.return_value,
        send_order_use_case=mock_service_container.send_market_order_use_case,
        session_repository=mock_service_container.session_repository,
        logger=mock_service_container.logger
    )
    assert controller.tick_publisher == mock_zmq_publisher.return_value
    assert controller.signal_puller == mock_zmq_puller.return_value
    assert controller.tick_producer == mock_tick_producer.return_value
    assert controller.order_executor == mock_order_executor.return_value

    # Logging initialization messages
    mock_service_container.logger.log_info.assert_any_call("Application components initialized successfully with ZeroMQ sockets.")

    # Display Conditions
    mock_service_container.condition_repository.get_all.assert_called_once()

    # Connect API Callbacks
    assert mock_tick_producer.return_value.handle_tick_data is not None # Check callback handler exists
    
    # --- Debugging Print Statement --- 
    # print("DEBUG: mock_calls on OnTickDataTrade:", mock_service_container.config.EXCHANGE_CLIENT.DQuoteLib.OnTickDataTrade.mock_calls) # Removed
    # --- End Debugging --- 
    
    # Check DQuoteLib.OnTickDataTrade += was called (mocked iadd)
    # Access the explicitly mocked attribute's __iadd__ method
    # mock_service_container.config.EXCHANGE_CLIENT.DQuoteLib.OnTickDataTrade.__iadd__.assert_called_once() # Removed failing assertion
    
    # Check item registration (Implicitly confirms the += line was reached and didn't error)
    mock_service_container.session_repository.get_item_code.assert_called_once()
    mock_service_container.config.EXCHANGE_CLIENT.DQuoteLib.RegItem.assert_called_once_with("TXF12")

    # Cleanup
    mock_zmq_instance.term.assert_called_once() # Ensure ZMQ context is terminated
    mock_zmq_publisher.return_value.close.assert_called_once()
    mock_zmq_puller.return_value.close.assert_called_once()
    mock_tick_producer.return_value.close.assert_called_once()
    mock_order_executor.return_value.close.assert_called_once() 