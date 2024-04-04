from src.app.cli_pfcf.controllers.select_order_account_controller import SelectOrderAccountController
from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


def test_get_user_input(monkeypatch, mocker, fixture_select_order_account):
    index_input = fixture_select_order_account["index_input"]
    order_account = fixture_select_order_account["order_account"]

    # manually set the user inputs
    fake_user_inputs = iter([index_input])
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))

    # initialize the RegisterItemController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.user_login_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.config.EXCHANGE_CLIENT.UserOrderSet = ["12345678900", "12345678901"]
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")

    input_dto = SelectOrderAccountController(service_container_mock)._get_user_input()

    assert input_dto.index == 0
    assert input_dto.order_account == order_account


def test_execute(mocker, fixture_select_order_account):
    # initialize the RegisterItemController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.user_login_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")
    service_container_mock.session_repository.is_user_logged_in.return_value = True

    # mock the module in execute
    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.select_order_account_controller.SelectOrderAccountPresenter')
    mock_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.select_order_account_controller.SelectOrderAccountUseCase')
    mock_use_case_instance = mock_use_case.return_value
    mock_view = mocker.patch(
        'src.app.cli_pfcf.controllers.select_order_account_controller.SelectOrderAccountView')

    result_use_case = {
        "action": "select_order_account",
        "message": "Order account selected successfully",
        "index": 1,
        "order_account": "12345678900",
    }

    mock_use_case_instance.execute.return_value = result_use_case
    mock_view_instance = mock_view.return_value

    input_dto = SelectOrderAccountInputDto(
        index=fixture_select_order_account["index"],
        order_account=fixture_select_order_account["order_account"]
    )

    controller = SelectOrderAccountController(service_container_mock)
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
