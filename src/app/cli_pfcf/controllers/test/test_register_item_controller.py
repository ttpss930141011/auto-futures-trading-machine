# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.app.cli_pfcf.controllers.register_item_controller import RegisterItemController
from src.interactor.dtos.register_item_dtos import RegisterItemInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.session_manager.session_manager import SessionManagerInterface


def test_register_item_event_handler(mocker):
    fake_emission_data = {
        "commodity_id": "TX00",
        "info_time": "08:45:00",
        "match_time": "08:45:00",
        "match_price": 12345,
        "match_buy_cnt": 1,
        "match_sell_cnt": 1,
        "match_quantity": 1,
        "match_total_qty": 1,
        "match_price_data": [1, 2, 3],
        "match_qty_data": [1, 2, 3]
    }

    # initialize the RegisterItemController
    logger_mock = None
    config_mock = None
    session_manager_mock = None

    # mock the module in execute method

    mock_view = mocker.patch(
        'src.app.cli_pfcf.controllers.register_item_controller.OnTickDataTradeView')
    mock_view_instance = mock_view.return_value
    mock_view_instance.show = mocker.MagicMock()

    controller = RegisterItemController(logger_mock, config_mock, session_manager_mock)
    result = controller._event_handler(
        commodity_id=fake_emission_data["commodity_id"],
        info_time=fake_emission_data["info_time"],
        match_time=fake_emission_data["match_time"],
        match_price=fake_emission_data["match_price"],
        match_buy_cnt=fake_emission_data["match_buy_cnt"],
        match_sell_cnt=fake_emission_data["match_sell_cnt"],
        match_quantity=fake_emission_data["match_quantity"],
        match_total_qty=fake_emission_data["match_total_qty"],
        match_price_data=fake_emission_data["match_price_data"],
        match_qty_data=fake_emission_data["match_qty_data"]
    )

    assert result == (fake_emission_data["match_price_data"], fake_emission_data["match_qty_data"])
    mock_view_instance.show.assert_called_once_with({
        "commodity_id": fake_emission_data["commodity_id"],
        "info_time": fake_emission_data["info_time"],
        "match_time": fake_emission_data["match_time"],
        "match_price": fake_emission_data["match_price"],
        "match_buy_cnt": fake_emission_data["match_buy_cnt"],
        "match_sell_cnt": fake_emission_data["match_sell_cnt"],
        "match_quantity": fake_emission_data["match_quantity"],
        "match_total_qty": fake_emission_data["match_total_qty"],
    })


def test_register_item(monkeypatch, mocker, fixture_register_item):
    # initialize the RegisterItemController
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    config_mock = mocker.patch('src.app.cli_pfcf.controllers.register_item_controller.Config')
    session_manager_mock = mocker.patch.object(SessionManagerInterface, "is_user_logged_in")
    session_manager_mock.get_current_user.return_value = fixture_register_item["account"]
    session_manager_mock.is_user_logged_in.return_value = True

    # manually set the user inputs
    item_code = fixture_register_item["item_code"]
    fake_user_inputs = iter([item_code])
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))

    # mock the module in execute method

    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.register_item_controller.RegisterItemPresenter')
    mock_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.register_item_controller.RegisterItemUseCase')
    mock_use_case_instance = mock_use_case.return_value
    mock_view = mocker.patch(
        'src.app.cli_pfcf.controllers.register_item_controller.RegisterItemView')
    mock_event_handler = mocker.patch(
        'src.app.cli_pfcf.controllers.register_item_controller.RegisterItemController._event_handler')

    result_use_case = {
        "action": "register_item",
        "message": "User registered successfully",
    }
    mock_use_case_instance.execute.return_value = result_use_case
    mock_view_instance = mock_view.return_value

    controller = RegisterItemController(logger_mock, config_mock, session_manager_mock)
    controller.execute()

    session_manager_mock.get_current_user.assert_called_once_with()
    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value,
        config_mock,
        logger_mock,
        session_manager_mock,
        mock_event_handler
    )
    input_dto = RegisterItemInputDto(account=fixture_register_item["account"], item_code=item_code)
    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    mock_view_instance.show.assert_called_once_with(result_use_case)


def test_register_item_with_no_login(monkeypatch, mocker, fixture_register_item):
    # initialize the RegisterItemController
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    config_mock = mocker.patch('src.app.cli_pfcf.controllers.register_item_controller.Config')
    session_manager_mock = mocker.patch.object(SessionManagerInterface, "is_user_logged_in")
    session_manager_mock.is_user_logged_in.return_value = False

    # manually set the user inputs
    item_code = fixture_register_item["item_code"]
    fake_user_inputs = iter([item_code])
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))

    # mock the module in execute method

    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.register_item_controller.RegisterItemPresenter')

    controller = RegisterItemController(logger_mock, config_mock, session_manager_mock)
    controller.execute()

    session_manager_mock.is_user_logged_in.assert_called_once_with()
    logger_mock.log_info.assert_called_once_with("User not login")

    mock_presenter.assert_not_called()
