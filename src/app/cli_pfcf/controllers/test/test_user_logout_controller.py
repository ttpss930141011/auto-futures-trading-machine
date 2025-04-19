# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
from typing import TYPE_CHECKING

from src.app.cli_pfcf.controllers.user_logout_controller import UserLogoutController
from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


def test_user_logout_success(mocker: 'MockerFixture', fixture_user):
    """ Test user logout successfully when logged in
    """
    account = fixture_user["account"]

    # Mock ServiceContainer and its dependencies
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.user_logout_controller.ServiceContainer')
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    config_mock = mocker.patch('src.app.cli_pfcf.config.Config')
    session_repository_mock = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")

    service_container_mock.logger = logger_mock
    service_container_mock.config = config_mock
    service_container_mock.session_repository = session_repository_mock

    # Setup session repository mocks for logged-in state
    session_repository_mock.is_user_logged_in.return_value = True
    session_repository_mock.get_current_user.return_value = account

    # Mock the components used within the controller's execute method
    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutPresenter')
    mock_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutUseCase')
    mock_use_case_instance = mock_use_case.return_value
    mock_view = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutView')
    mock_view_instance = mock_view.return_value

    # Define the expected result from the use case
    result_use_case = {
        "action": "user_logout",
        "message": "User logged out successfully",
        "account": account,
    }
    mock_use_case_instance.execute.return_value = result_use_case

    # Instantiate and execute the controller
    controller = UserLogoutController(service_container_mock)
    controller.execute()

    # Assertions
    session_repository_mock.is_user_logged_in.assert_called_once_with()
    session_repository_mock.get_current_user.assert_called_once_with()
    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value,
        config_mock,
        logger_mock,
        session_repository_mock
    )
    input_dto = UserLogoutInputDto(account=account)
    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    mock_view.assert_called_once_with()
    mock_view_instance.show.assert_called_once_with(result_use_case)
    logger_mock.log_info.assert_not_called() # Ensure "User not login" wasn't logged


def test_user_logout_when_not_logged_in(mocker: 'MockerFixture'):
    """ Test user logout attempt when not logged in
    """
    # Mock ServiceContainer and its dependencies
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.user_logout_controller.ServiceContainer')
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    session_repository_mock = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")

    service_container_mock.logger = logger_mock
    service_container_mock.session_repository = session_repository_mock

    # Setup session repository mocks for logged-out state
    session_repository_mock.is_user_logged_in.return_value = False

    # Mock components that should NOT be called
    mock_presenter = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutPresenter')
    mock_use_case = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutUseCase')
    mock_view = mocker.patch(
        'src.app.cli_pfcf.controllers.user_logout_controller.UserLogoutView')

    # Instantiate and execute the controller
    controller = UserLogoutController(service_container_mock)
    controller.execute()

    # Assertions
    session_repository_mock.is_user_logged_in.assert_called_once_with()
    session_repository_mock.get_current_user.assert_not_called()
    logger_mock.log_info.assert_called_once_with("User not login")
    mock_presenter.assert_not_called()
    mock_use_case.assert_not_called()
    mock_view.assert_not_called()
