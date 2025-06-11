import pytest
from unittest.mock import MagicMock

from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountInputDto, SelectOrderAccountOutputDto
from src.interactor.errors.error_classes import LoginFailedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.select_order_account_presenter import SelectOrderAccountPresenterInterface
from src.interactor.use_cases.select_order_account import SelectOrderAccountUseCase


def test_select_order_account(fixture_select_order_account):
    # mock all dependencies in the use case
    mock_presenter = MagicMock(spec=SelectOrderAccountPresenterInterface)
    mock_service_container = MagicMock()
    mock_service_container.exchange_client.UserOrderSet = ["12345678900", "12345678901"]
    mock_service_container.session_repository.get_current_user.return_value = "Test user"
    mock_service_container.session_repository.set_order_account_set.return_value = "Test order account set"
    mock_service_container.session_repository.set_order_account.return_value = "Test order account"

    from src.interactor.validations.select_order_account_validator import SelectOrderAccountInputDtoValidator
    mock_validator = MagicMock(spec=SelectOrderAccountInputDtoValidator)
    mock_presenter.present.return_value = "Test output"

    use_case = SelectOrderAccountUseCase(
        mock_presenter,
        mock_service_container,
    )

    input_dto = SelectOrderAccountInputDto(
        index=fixture_select_order_account["index"],
        order_account=fixture_select_order_account["order_account"]
    )
    
    # Mock the validator creation
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.interactor.use_cases.select_order_account.SelectOrderAccountInputDtoValidator", lambda x: mock_validator)
        result = use_case.execute(input_dto)

    mock_validator.validate.assert_called_once_with()

    mock_service_container.session_repository.get_current_user.assert_called_once()

    mock_service_container.session_repository.set_order_account_set.assert_called_once_with(mock_service_container.exchange_client.UserOrderSet)
    mock_service_container.session_repository.set_order_account.assert_called_once_with(fixture_select_order_account["order_account"])

    output_dto = SelectOrderAccountOutputDto(
        is_select_order_account=True,
        order_account=fixture_select_order_account["order_account"]
    )

    mock_presenter.present.assert_called_once_with(output_dto)
    mock_service_container.logger.log_info.assert_called_once_with(f"Order account {input_dto.order_account} selected")

    assert result == "Test output"


def test_select_order_account_if_user_is_none(fixture_select_order_account):
    # mock all dependencies in the use case
    mock_presenter = MagicMock(spec=SelectOrderAccountPresenterInterface)
    mock_service_container = MagicMock()
    mock_service_container.exchange_client.UserOrderSet = ["12345678900", "12345678901"]
    mock_service_container.session_repository.get_current_user.return_value = None
    mock_service_container.session_repository.set_order_account_set.return_value = "Test order account set"
    mock_service_container.session_repository.set_order_account.return_value = "Test order account"

    from src.interactor.validations.select_order_account_validator import SelectOrderAccountInputDtoValidator
    mock_validator = MagicMock(spec=SelectOrderAccountInputDtoValidator)
    mock_presenter.present.return_value = "Test output"

    use_case = SelectOrderAccountUseCase(
        mock_presenter,
        mock_service_container,
    )
    input_dto = SelectOrderAccountInputDto(
        index=fixture_select_order_account["index"],
        order_account=fixture_select_order_account["order_account"]
    )

    # Mock the validator creation
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.interactor.use_cases.select_order_account.SelectOrderAccountInputDtoValidator", lambda x: mock_validator)
        with pytest.raises(LoginFailedException) as exc:
            use_case.execute(input_dto)

    mock_validator.validate.assert_called_once_with()

    mock_service_container.session_repository.get_current_user.assert_called_once()

    assert str(exc.value) == "Login failed: User not logged in"