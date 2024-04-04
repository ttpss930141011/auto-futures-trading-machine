from src.app.cli_pfcf.controllers.send_market_order_controller import SendMarketOrderController
from src.domain.value_objects import OrderOperation, OrderTypeEnum, OpenClose, DayTrade, TimeInForce
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


def test_get_user_input(monkeypatch, mocker):
    side = "b"
    quantity = "10"

    # manually set the user inputs
    fake_user_inputs = iter([side, quantity])
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))

    # initialize the RegisterItemController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.user_login_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.session_repository = mocker.patch(
        'src.infrastructure.repositories.session_in_memory_repository.SessionInMemoryRepository')
    service_container_mock.session_repository.get_order_account.return_value = "12345678900"
    service_container_mock.session_repository.get_item_code.return_value = "TXFD88"

    input_dto = SendMarketOrderController(service_container_mock)._get_user_input()

    assert input_dto.order_account == "12345678900"
    assert input_dto.item_code == "TXFD88"
    assert input_dto.side == OrderOperation.BUY
    assert input_dto.order_type == OrderTypeEnum.Market
    assert input_dto.price == 0
    assert input_dto.quantity == 10
    assert input_dto.open_close == OpenClose.AUTO
    assert input_dto.note == ""
    assert input_dto.day_trade == DayTrade.No
    assert input_dto.time_in_force == TimeInForce.IOC


def test_execute(mocker, fixture_send_market_order):
    # initialize the RegisterItemController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.user_login_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")
    service_container_mock.session_repository.is_user_logged_in.return_value = True

    # mock the module in execute
    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.send_market_order_controller.SendMarketOrderPresenter')
    mock_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.send_market_order_controller.SendMarketOrderUseCase')
    mock_use_case_instance = mock_use_case.return_value
    mock_view = mocker.patch(
        'src.app.cli_pfcf.controllers.send_market_order_controller.SendMarketOrderView')

    result_use_case = {
        "action": "send_market_order",
        "message": f"Order with serial {fixture_send_market_order['order_account']} is send: True",
        "note": "",
        "order_serial": fixture_send_market_order['order_account'],
    }

    mock_use_case_instance.execute.return_value = result_use_case
    mock_view_instance = mock_view.return_value

    input_dto = SendMarketOrderInputDto(**fixture_send_market_order)

    controller = SendMarketOrderController(service_container_mock)
    controller._get_user_input = mocker.MagicMock()
    controller._get_user_input.return_value = input_dto
    controller.execute()

    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value,
        service_container_mock.config,
        service_container_mock.logger,
        service_container_mock.session_repository
    )

    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    mock_view_instance.show.assert_called_once_with(result_use_case)
