# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
from typing import TYPE_CHECKING

from src.app.cli_pfcf.controllers.show_futures_controller import ShowFuturesController
from src.interactor.dtos.show_futures_dtos import ShowFuturesInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture
    from _pytest.monkeypatch import MonkeyPatch


def test_show_futures_success_all(
    mocker: "MockerFixture", monkeypatch: "MonkeyPatch", fixture_user
):
    """Test showing all futures successfully when logged in."""
    account = fixture_user["account"]
    futures_code_input = ""  # User inputs empty string for all futures

    # Mock user input
    monkeypatch.setattr("builtins.input", lambda _: futures_code_input)

    # Mock ServiceContainer and its dependencies
    service_container_mock = mocker.patch(
        "src.app.cli_pfcf.controllers.show_futures_controller.ServiceContainer"
    )
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    config_mock = mocker.patch("src.app.cli_pfcf.config.Config")
    session_repository_mock = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")

    service_container_mock.logger = logger_mock
    service_container_mock.config = config_mock
    service_container_mock.session_repository = session_repository_mock

    # Setup session repository mocks for logged-in state
    session_repository_mock.is_user_logged_in.return_value = True
    session_repository_mock.get_current_user.return_value = account

    # Mock the components used within the controller's execute method
    mock_presenter = mocker.patch(
        "src.app.cli_pfcf.controllers.show_futures_controller.ShowFuturesPresenter"
    )
    mock_use_case = mocker.patch(
        "src.app.cli_pfcf.controllers.show_futures_controller.ShowFuturesUseCase"
    )
    mock_use_case_instance = mock_use_case.return_value
    mock_view = mocker.patch("src.app.cli_pfcf.controllers.show_futures_controller.ShowFuturesView")
    mock_view_instance = mock_view.return_value

    # Define the expected result from the use case
    result_use_case = {
        "action": "show_futures",
        "message": "Futures data retrieved successfully",
        "data": [{"code": "TXF", "price": 18000}, {"code": "MXF", "price": 3000}],
    }
    mock_use_case_instance.execute.return_value = result_use_case

    # Instantiate and execute the controller
    controller = ShowFuturesController(service_container_mock)
    controller.execute()

    # Assertions
    session_repository_mock.is_user_logged_in.assert_called_once_with()
    session_repository_mock.get_current_user.assert_called_once_with()
    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value, service_container_mock
    )
    input_dto = ShowFuturesInputDto(account=account, futures_code=futures_code_input)
    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    mock_view.assert_called_once_with()
    mock_view_instance.show.assert_called_once_with(result_use_case)
    logger_mock.log_info.assert_not_called()  # Ensure "User not logged in" wasn't logged


def test_show_futures_success_specific(
    mocker: "MockerFixture", monkeypatch: "MonkeyPatch", fixture_user
):
    """Test showing specific future successfully when logged in."""
    account = fixture_user["account"]
    futures_code_input = "TXF"  # User inputs specific code

    # Mock user input
    monkeypatch.setattr("builtins.input", lambda _: futures_code_input)

    # Mock ServiceContainer and dependencies (similar to above, could be refactored into a fixture)
    service_container_mock = mocker.patch(
        "src.app.cli_pfcf.controllers.show_futures_controller.ServiceContainer"
    )
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    config_mock = mocker.patch("src.app.cli_pfcf.config.Config")
    session_repository_mock = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")

    service_container_mock.logger = logger_mock
    service_container_mock.config = config_mock
    service_container_mock.session_repository = session_repository_mock

    session_repository_mock.is_user_logged_in.return_value = True
    session_repository_mock.get_current_user.return_value = account

    mock_presenter = mocker.patch(
        "src.app.cli_pfcf.controllers.show_futures_controller.ShowFuturesPresenter"
    )
    mock_use_case = mocker.patch(
        "src.app.cli_pfcf.controllers.show_futures_controller.ShowFuturesUseCase"
    )
    mock_use_case_instance = mock_use_case.return_value
    mock_view = mocker.patch("src.app.cli_pfcf.controllers.show_futures_controller.ShowFuturesView")
    mock_view_instance = mock_view.return_value

    result_use_case = {
        "action": "show_futures",
        "message": "Futures data retrieved successfully",
        "data": [{"code": "TXF", "price": 18000}],
    }
    mock_use_case_instance.execute.return_value = result_use_case

    controller = ShowFuturesController(service_container_mock)
    controller.execute()

    session_repository_mock.is_user_logged_in.assert_called_once_with()
    session_repository_mock.get_current_user.assert_called_once_with()
    mock_presenter.assert_called_once_with()
    mock_use_case.assert_called_once_with(
        mock_presenter.return_value, service_container_mock
    )
    input_dto = ShowFuturesInputDto(account=account, futures_code=futures_code_input)
    mock_use_case_instance.execute.assert_called_once_with(input_dto)
    mock_view.assert_called_once_with()
    mock_view_instance.show.assert_called_once_with(result_use_case)
    logger_mock.log_info.assert_not_called()


def test_show_futures_when_not_logged_in(mocker: "MockerFixture"):
    """Test showing futures attempt when not logged in"""
    # Mock ServiceContainer and its dependencies
    service_container_mock = mocker.patch(
        "src.app.cli_pfcf.controllers.show_futures_controller.ServiceContainer"
    )
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    session_repository_mock = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")

    service_container_mock.logger = logger_mock
    service_container_mock.session_repository = session_repository_mock

    # Setup session repository mocks for logged-out state
    session_repository_mock.is_user_logged_in.return_value = False

    # Mock components that should NOT be called
    mock_presenter = mocker.patch(
        "src.app.cli_pfcf.controllers.show_futures_controller.ShowFuturesPresenter"
    )
    mock_use_case = mocker.patch(
        "src.app.cli_pfcf.controllers.show_futures_controller.ShowFuturesUseCase"
    )
    mock_view = mocker.patch("src.app.cli_pfcf.controllers.show_futures_controller.ShowFuturesView")

    # Instantiate and execute the controller
    controller = ShowFuturesController(service_container_mock)
    controller.execute()

    # Assertions
    session_repository_mock.is_user_logged_in.assert_called_once_with()
    session_repository_mock.get_current_user.assert_not_called()
    logger_mock.log_info.assert_called_once_with("User not logged in")
    mock_presenter.assert_not_called()
    mock_use_case.assert_not_called()
    mock_view.assert_not_called()
