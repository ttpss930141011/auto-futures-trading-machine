# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.app.cli_pfcf.controllers.register_item_controller import RegisterItemController
from src.interactor.dtos.register_item_dtos import RegisterItemInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


def test_register_item(monkeypatch, mocker, fixture_register_item):
    # initialize the RegisterItemController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.register_item_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")
    service_container_mock.session_repository.get_current_user.return_value = fixture_register_item["account"]
    service_container_mock.session_repository.is_user_logged_in.return_value = True

    logger_mock = service_container_mock.logger
    config_mock = service_container_mock.config
    session_manager_mock = service_container_mock.session_repository

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

    result_use_case = {
        "action": "register_item",
        "message": "User registered successfully",
    }
    mock_use_case_instance.execute.return_value = result_use_case
    mock_view_instance = mock_view.return_value

    controller = RegisterItemController(service_container_mock)
    controller.execute()

    session_manager_mock.get_current_user.assert_called_once_with()
    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value,
        service_container_mock,
    )
    input_dto = RegisterItemInputDto(account=fixture_register_item["account"], item_code=item_code)
    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    mock_view_instance.show.assert_called_once_with(result_use_case)


def test_register_item_with_no_login(monkeypatch, mocker, fixture_register_item):
    # initialize the RegisterItemController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.register_item_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")
    service_container_mock.session_repository.get_current_user.return_value = fixture_register_item["account"]
    service_container_mock.session_repository.is_user_logged_in.return_value = False

    logger_mock = service_container_mock.logger
    session_manager_mock = service_container_mock.session_repository

    # manually set the user inputs
    item_code = fixture_register_item["item_code"]
    fake_user_inputs = iter([item_code])
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))

    # mock the module in execute method

    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.register_item_controller.RegisterItemPresenter')

    controller = RegisterItemController(service_container_mock)
    controller.execute()

    session_manager_mock.is_user_logged_in.assert_called_once_with()
    logger_mock.log_info.assert_called_once_with("User not login")

    mock_presenter.assert_not_called()
