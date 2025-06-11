from unittest.mock import MagicMock, patch

from src.app.cli_pfcf.controllers.select_order_account_controller import SelectOrderAccountController
from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


def test_get_user_input(monkeypatch, fixture_select_order_account):
    index_input = fixture_select_order_account["index_input"]
    order_account = fixture_select_order_account["order_account"]

    # manually set the user inputs
    fake_user_inputs = iter([index_input])
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))

    # Create service container mock
    service_container_mock = MagicMock()
    service_container_mock.logger = MagicMock(spec=LoggerInterface)
    service_container_mock.exchange_client.UserOrderSet = ["12345678900", "12345678901"]
    service_container_mock.session_repository = MagicMock(spec=SessionRepositoryInterface)

    input_dto = SelectOrderAccountController(service_container_mock)._get_user_input()

    assert input_dto.index == 0
    assert input_dto.order_account == order_account


def test_execute(fixture_select_order_account):
    # Create service container mock
    service_container_mock = MagicMock()
    service_container_mock.logger = MagicMock(spec=LoggerInterface)
    service_container_mock.session_repository = MagicMock(spec=SessionRepositoryInterface)
    service_container_mock.session_repository.is_user_logged_in.return_value = True

    # Mock the modules in execute
    with patch('src.app.cli_pfcf.controllers.select_order_account_controller.SelectOrderAccountPresenter') as mock_presenter, \
         patch('src.app.cli_pfcf.controllers.select_order_account_controller.SelectOrderAccountUseCase') as mock_use_case, \
         patch('src.app.cli_pfcf.controllers.select_order_account_controller.SelectOrderAccountView') as mock_view:

        mock_use_case_instance = mock_use_case.return_value
        mock_view_instance = mock_view.return_value

        result_use_case = {
            "action": "select_order_account",
            "message": "Order account selected successfully",
            "index": 1,
            "order_account": "12345678900",
        }

        mock_use_case_instance.execute.return_value = result_use_case

        input_dto = SelectOrderAccountInputDto(
            index=fixture_select_order_account["index"],
            order_account=fixture_select_order_account["order_account"]
        )

        controller = SelectOrderAccountController(service_container_mock)
        controller._get_user_input = MagicMock()
        controller._get_user_input.return_value = input_dto
        controller.execute()

        mock_presenter.assert_called_once_with()
        mock_use_case.assert_called_once_with(
            mock_presenter.return_value,
            service_container_mock
        )

        mock_use_case_instance.execute.assert_called_once_with(input_dto)
        mock_view_instance.show.assert_called_once_with(result_use_case)
