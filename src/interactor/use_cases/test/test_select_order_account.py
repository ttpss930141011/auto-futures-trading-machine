import pytest

from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountInputDto, SelectOrderAccountOutputDto
from src.interactor.errors.error_classes import LoginFailedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.select_order_account_presenter import SelectOrderAccountPresenterInterface
from src.interactor.use_cases.select_order_account import SelectOrderAccountUseCase


def test_select_order_account(mocker, fixture_select_order_account):
    # mock all dependencies in the use case
    mock_presenter = mocker.patch.object(SelectOrderAccountPresenterInterface, "present")
    mock_config = mocker.patch("src.app.cli_pfcf.config.Config")
    mock_config.EXCHANGE_CLIENT.UserOrderSet = ["12345678900", "12345678901"]
    mock_logger = mocker.patch.object(LoggerInterface, "log_info")
    mock_session_repository = mocker.patch(
        "src.infrastructure.repositories.session_in_memory_repository.SessionInMemoryRepository")
    mock_session_repository.get_current_user.return_value = "Test user"
    mock_session_repository.set_order_account_set = mocker.MagicMock()
    mock_session_repository.set_order_account_set.return_value = "Test order account set"
    mock_session_repository.set_order_account = mocker.MagicMock()
    mock_session_repository.set_order_account.return_value = "Test order account"

    mock_validator = mocker.patch("src.interactor.use_cases.select_order_account.SelectOrderAccountInputDtoValidator")
    mock_validator_instance = mock_validator.return_value
    mock_presenter.present.return_value = "Test output"
    mock_session_repository.return_value = "Test user"

    use_case = SelectOrderAccountUseCase(
        mock_presenter,
        mock_config,
        mock_logger,
        mock_session_repository,
    )

    input_dto = SelectOrderAccountInputDto(
        index=fixture_select_order_account["index"],
        order_account=fixture_select_order_account["order_account"]
    )
    result = use_case.execute(input_dto)

    mock_validator.assert_called_once_with(input_dto.to_dict())
    mock_validator_instance.validate.assert_called_once_with()

    mock_session_repository.get_current_user.assert_called_once()

    mock_session_repository.set_order_account_set.assert_called_once_with(mock_config.EXCHANGE_CLIENT.UserOrderSet)
    mock_session_repository.set_order_account.assert_called_once_with(fixture_select_order_account["order_account"])

    output_dto = SelectOrderAccountOutputDto(
        is_select_order_account=True,
        order_account=fixture_select_order_account["order_account"]
    )

    mock_presenter.present.assert_called_once_with(output_dto)
    mock_logger.log_info.assert_called_once_with(f"Order account {input_dto.order_account} selected")

    assert result == "Test output"


def test_select_order_account_if_user_is_none(mocker, fixture_select_order_account):
    # mock all dependencies in the use case
    mock_presenter = mocker.patch.object(SelectOrderAccountPresenterInterface, "present")
    mock_config = mocker.patch("src.app.cli_pfcf.config.Config")
    mock_config.EXCHANGE_CLIENT.UserOrderSet = ["12345678900", "12345678901"]
    mock_logger = mocker.patch.object(LoggerInterface, "log_info")
    mock_session_repository = mocker.patch(
        "src.infrastructure.repositories.session_in_memory_repository.SessionInMemoryRepository")
    mock_session_repository.get_current_user.return_value = None
    mock_session_repository.set_order_account_set = mocker.MagicMock()
    mock_session_repository.set_order_account_set.return_value = "Test order account set"
    mock_session_repository.set_order_account = mocker.MagicMock()
    mock_session_repository.set_order_account.return_value = "Test order account"

    mock_validator = mocker.patch("src.interactor.use_cases.select_order_account.SelectOrderAccountInputDtoValidator")
    mock_validator_instance = mock_validator.return_value
    mock_presenter.present.return_value = "Test output"
    mock_session_repository.return_value = "Test user"

    use_case = SelectOrderAccountUseCase(
        mock_presenter,
        mock_config,
        mock_logger,
        mock_session_repository,
    )
    input_dto = SelectOrderAccountInputDto(
        index=fixture_select_order_account["index"],
        order_account=fixture_select_order_account["order_account"]
    )

    with pytest.raises(LoginFailedException) as exc:
        use_case.execute(input_dto)

    mock_validator.assert_called_once_with(input_dto.to_dict())
    mock_validator_instance.validate.assert_called_once_with()

    mock_session_repository.get_current_user.assert_called_once()

    assert str(exc.value) == "Login failed: User not logged in"
