# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.app.cli_pfcf.controllers.user_login_controller import UserLoginController
from src.interactor.dtos.user_login_dtos import UserLoginInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.session_manager.session_manager import SessionManagerInterface


def test_user_login(monkeypatch, mocker, fixture_user):
    account = fixture_user["account"]
    password = fixture_user["password"]
    ip_address = fixture_user["ip_address"]

    # manually set the user inputs
    fake_user_inputs = iter([account, password, ip_address])
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))

    mock_repository = mocker.patch(
        'src.app.cli_pfcf.controllers.user_login_controller.UserInMemoryRepository')
    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.user_login_controller.UserLoginPresenter')
    mock_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.user_login_controller.UserLoginUseCase')
    mock_use_case_instance = mock_use_case.return_value
    mock_view = mocker.patch(
        'src.app.cli_pfcf.controllers.user_login_controller.UserLoginView')
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    config_mock = mocker.patch('src.app.cli_pfcf.controllers.user_login_controller.Config')
    config_mock.DEALER_TEST_URL = ip_address
    session_manager_mock = mocker.patch.object(SessionManagerInterface, "is_user_logged_in")
    session_manager_mock.is_user_logged_in.return_value = False

    result_use_case = {
        "action": "user_login",
        "message": "User logged in successfully",
        "account": account,
        "ip_address": ip_address,
    }
    mock_use_case_instance.execute.return_value = result_use_case
    mock_view_instance = mock_view.return_value

    controller = UserLoginController(logger_mock, config_mock, session_manager_mock)
    controller.execute()

    mock_repository.assert_called_once_with()
    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value,
        mock_repository.return_value,
        config_mock,
        logger_mock,
        session_manager_mock
    )
    input_dto = UserLoginInputDto(account, password, ip_address)
    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    mock_view_instance.show.assert_called_once_with(result_use_case)
