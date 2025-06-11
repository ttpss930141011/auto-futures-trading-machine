# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.app.cli_pfcf.controllers.user_login_controller import UserLoginController
from src.interactor.dtos.user_login_dtos import UserLoginInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


def test_user_login(monkeypatch, mocker, fixture_user):
    account = fixture_user["account"]
    password = fixture_user["password"]
    is_production = "n"
    ip_address = fixture_user["ip_address"]

    # manually set the user inputs
    fake_user_inputs = iter([account, password, is_production])
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))
    # monkeypatch.setattr('getpass.getpass', lambda _: password)  # Mock getpass - Replaced
    mock_getpass = mocker.patch('src.app.cli_pfcf.controllers.user_login_controller.getpass')
    mock_getpass.return_value = password

    # initialize the RegisterItemController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.user_login_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")
    service_container_mock.session_repository.get_current_user.return_value = account
    service_container_mock.session_repository.is_user_logged_in.return_value = False

    logger_mock = service_container_mock.logger
    config_mock = service_container_mock.config
    config_mock.EXCHANGE_TEST_URL = fixture_user["ip_address"]
    session_repository_mock = service_container_mock.session_repository

    # mock the module in use case
    mock_repository = mocker.patch(
        'src.app.cli_pfcf.controllers.user_login_controller.UserInMemoryRepository')
    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.user_login_controller.UserLoginPresenter')
    mock_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.user_login_controller.UserLoginUseCase')
    mock_use_case_instance = mock_use_case.return_value
    mock_view = mocker.patch(
        'src.app.cli_pfcf.controllers.user_login_controller.UserLoginView')

    result_use_case = {
        "action": "user_login",
        "message": "User logged in successfully",
        "account": account,
        "ip_address": ip_address,
    }
    mock_use_case_instance.execute.return_value = result_use_case
    mock_view_instance = mock_view.return_value

    controller = UserLoginController(service_container_mock)
    controller.execute()

    mock_repository.assert_called_once_with()
    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value,
        mock_repository.return_value,
        service_container_mock,
        logger_mock,
        session_repository_mock
    )
    input_dto = UserLoginInputDto(account, password, ip_address)
    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    mock_view_instance.show.assert_called_once_with(result_use_case)
    mock_getpass.assert_called_once_with("Enter the password: ")


def test_user_login_with_user_already_logged_in(monkeypatch, mocker, fixture_user):
    # initialize the RegisterItemController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.user_login_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")
    service_container_mock.session_repository.is_user_logged_in.return_value = True
    logger_mock = service_container_mock.logger
    session_repository_mock = service_container_mock.session_repository

    # mock the module in use case to make sure it is not called
    mock_repository = mocker.patch(
        'src.app.cli_pfcf.controllers.user_login_controller.UserInMemoryRepository')

    # execute the controller
    controller = UserLoginController(service_container_mock)
    controller.execute()

    # assert the results
    session_repository_mock.is_user_logged_in.assert_called_once_with()
    logger_mock.log_info.assert_called_once_with("User already logged in")
    mock_repository.assert_not_called()
