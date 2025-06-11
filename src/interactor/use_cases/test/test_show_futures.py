# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name # for pytest fixtures

import pytest
from unittest.mock import MagicMock
from typing import TYPE_CHECKING, List, Dict, Any

# Imports for types being tested/mocked
from src.interactor.use_cases.show_futures import ShowFuturesUseCase
from src.interactor.dtos.show_futures_dtos import (
    ShowFuturesInputDto,
    ShowFuturesOutputDto,
)
from src.interactor.interfaces.presenters.show_futures_presenter import (
    ShowFuturesPresenterInterface,
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface

# Conditional imports for type checking
if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture

# --- Fixtures ---


@pytest.fixture
def mock_presenter() -> MagicMock:
    """Fixture for a mocked ShowFuturesPresenterInterface."""
    return MagicMock(spec=ShowFuturesPresenterInterface)


@pytest.fixture
def mock_logger() -> MagicMock:
    """Fixture for a mocked LoggerInterface."""
    return MagicMock(spec=LoggerInterface)


@pytest.fixture
def mock_session_repo() -> MagicMock:
    """Fixture for a mocked SessionRepositoryInterface."""
    repo = MagicMock(spec=SessionRepositoryInterface)
    repo.is_user_logged_in.return_value = True  # Default to logged in
    return repo


@pytest.fixture
def mock_service_container() -> MagicMock:
    """Fixture for a mocked service container containing a mocked API client."""
    mock_api_client = MagicMock(name="PFCFApiClient")
    mock_api_client.PFCGetFutureData = MagicMock(name="PFCGetFutureData")

    mock_container = MagicMock()
    mock_container.exchange_client = mock_api_client
    return mock_container


@pytest.fixture
def show_futures_use_case(
    mock_presenter, mock_service_container, mock_logger, mock_session_repo
) -> ShowFuturesUseCase:
    """Fixture to create a ShowFuturesUseCase instance with mocked dependencies."""
    return ShowFuturesUseCase(
        presenter=mock_presenter,
        service_container=mock_service_container,
    )


# --- Test Cases ---


def test_show_futures_success_all(
    show_futures_use_case: ShowFuturesUseCase,
    mock_presenter,
    mock_service_container,
    mock_logger,
    mock_session_repo,
):
    """Test successfully fetching all futures data."""
    # Arrange
    input_dto = ShowFuturesInputDto(account="test_acc", futures_code="")
    mock_api_data: List[Dict[str, Any]] = [
        {"code": "TXF1", "name": "TAIEX Futures 1"},
        {"code": "MXF1", "name": "Mini TAIEX 1"},
    ]
    expected_output = ShowFuturesOutputDto(
        success=True, message="Success", futures_data=mock_api_data
    )

    mock_service_container.exchange_client.PFCGetFutureData.return_value = mock_api_data
    mock_presenter.present_futures_data.return_value = expected_output

    # Act
    result = show_futures_use_case.execute(input_dto)

    # Assert
    assert result == expected_output
    mock_service_container.session_repository.is_user_logged_in.assert_called_once()
    mock_service_container.logger.log_info.assert_called_once_with("Getting futures data for code: ALL")
    mock_service_container.exchange_client.PFCGetFutureData.assert_called_once_with(
        ""
    )  # Called with empty string for ALL
    mock_presenter.present_futures_data.assert_called_once_with(mock_api_data)
    mock_presenter.present_error.assert_not_called()


def test_show_futures_success_specific(
    show_futures_use_case: ShowFuturesUseCase,
    mock_presenter,
    mock_service_container,
    mock_logger,
    mock_session_repo,
):
    """Test successfully fetching specific future data."""
    # Arrange
    specific_code = "TXF12"
    input_dto = ShowFuturesInputDto(account="test_acc", futures_code=specific_code)
    mock_api_data: List[Dict[str, Any]] = [{"code": "TXF12", "name": "TAIEX Futures 12"}]
    expected_output = ShowFuturesOutputDto(
        success=True, message="Success", futures_data=mock_api_data
    )

    mock_service_container.exchange_client.PFCGetFutureData.return_value = mock_api_data
    mock_presenter.present_futures_data.return_value = expected_output

    # Act
    result = show_futures_use_case.execute(input_dto)

    # Assert
    assert result == expected_output
    mock_service_container.session_repository.is_user_logged_in.assert_called_once()
    mock_service_container.logger.log_info.assert_called_once_with(f"Getting futures data for code: {specific_code}")
    mock_service_container.exchange_client.PFCGetFutureData.assert_called_once_with(specific_code)
    mock_presenter.present_futures_data.assert_called_once_with(mock_api_data)
    mock_presenter.present_error.assert_not_called()


def test_show_futures_not_logged_in(
    show_futures_use_case: ShowFuturesUseCase,
    mock_presenter,
    mock_service_container,
    mock_logger,
    mock_session_repo,
):
    """Test execution when the user is not logged in."""
    # Arrange
    input_dto = ShowFuturesInputDto(account="test_acc", futures_code="TXF12")
    error_message = "User not logged in"
    expected_output = ShowFuturesOutputDto(success=False, message=error_message)

    mock_service_container.session_repository.is_user_logged_in.return_value = False  # Simulate not logged in
    mock_presenter.present_error.return_value = expected_output

    # Act
    result = show_futures_use_case.execute(input_dto)

    # Assert
    assert result == expected_output
    mock_service_container.session_repository.is_user_logged_in.assert_called_once()
    mock_presenter.present_error.assert_called_once_with(error_message)
    mock_service_container.logger.log_info.assert_not_called()
    mock_service_container.exchange_client.PFCGetFutureData.assert_not_called()
    mock_presenter.present_futures_data.assert_not_called()


def test_show_futures_api_exception(
    show_futures_use_case: ShowFuturesUseCase,
    mock_presenter,
    mock_service_container,
    mock_logger,
    mock_session_repo,
):
    """Test handling of an exception during the API call."""
    # Arrange
    input_dto = ShowFuturesInputDto(account="test_acc", futures_code="ALL")
    api_error = Exception("Network timeout")
    expected_output = ShowFuturesOutputDto(success=False, message=str(api_error))

    mock_service_container.exchange_client.PFCGetFutureData.side_effect = api_error
    mock_presenter.present_error.return_value = expected_output

    # Act
    result = show_futures_use_case.execute(input_dto)

    # Assert
    assert result == expected_output
    mock_service_container.session_repository.is_user_logged_in.assert_called_once()
    mock_service_container.logger.log_info.assert_called_once_with(
        "Getting futures data for code: ALL"
    )  # Logging happens before call
    mock_service_container.exchange_client.PFCGetFutureData.assert_called_once_with("")
    mock_service_container.logger.log_error.assert_called_once_with(f"Error in ShowFuturesUseCase: {str(api_error)}")
    mock_presenter.present_error.assert_called_once_with(str(api_error))
    mock_presenter.present_futures_data.assert_not_called()
