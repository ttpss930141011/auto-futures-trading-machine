# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.app.cli_pfcf.controllers.user_logout_controller import UserLogoutController
from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


def test_user_logout(monkeypatch, mocker, fixture_user):
    # initialize the UserLogoutController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.register_item_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")
    service_container_mock.session_repository.get_current_user.return_value = fixture_user["account"]
    service_container_mock.session_repository.is_user_logged_in.return_value = True
    logger_mock = service_container_mock.logger
    config_mock = service_container_mock.config
    session_manager_mock = service_container_mock.session_repository


    # mock the items in execute
    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutPresenter')
    mock_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutUseCase')
    mock_use_case_instance = mock_use_case.return_value
    mock_view = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutView')

    result_use_case = {
        "action": "logout",
        "message": "User logout successfully",
        "account": fixture_user["account"],
        "is_success": True
    }
    mock_use_case_instance.execute.return_value = result_use_case
    mock_view_instance = mock_view.return_value

    # execute the controller
    controller = UserLogoutController(service_container_mock)
    controller.execute()

    # assert the mock
    session_manager_mock.is_user_logged_in.assert_called_once_with()
    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value,
        config_mock,
        logger_mock,
        session_manager_mock
    )
    input_dto = UserLogoutInputDto(account=fixture_user["account"])
    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    mock_view_instance.show.assert_called_once_with(result_use_case)


def test_user_logout_with_user_not_login(monkeypatch, mocker, fixture_user):
    # initialize the UserLogoutController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.register_item_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")
    service_container_mock.session_repository.get_current_user.return_value = fixture_user["account"]
    service_container_mock.session_repository.is_user_logged_in.return_value = False
    logger_mock = service_container_mock.logger
    config_mock = service_container_mock.config
    session_manager_mock = service_container_mock.session_repository

    # mock the items in execute
    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutPresenter')

    controller = UserLogoutController(service_container_mock)
    controller.execute()

    session_manager_mock.is_user_logged_in.assert_called_once_with()
    logger_mock.log_info.assert_called_once_with("User not login")

    mock_presenter.assert_not_called()
