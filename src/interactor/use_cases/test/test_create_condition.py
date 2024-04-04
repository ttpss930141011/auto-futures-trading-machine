import uuid

import pytest

from src.domain.entities.condition import Condition
from src.interactor.dtos.create_condition_dtos import CreateConditionInputDto, CreateConditionOutputDto
from src.interactor.errors.error_classes import LoginFailedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.create_condition_presenter import CreateConditionPresenterInterface
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.use_cases.create_condition import CreateConditionUseCase


def test_create_condition(mocker, fixture_create_condition):
    condition = Condition(
        condition_id=uuid.uuid4(),
        **fixture_create_condition
    )
    # mock all dependencies in the use case
    mock_presenter = mocker.patch.object(CreateConditionPresenterInterface, "present")
    mock_condition_repository = mocker.patch.object(ConditionRepositoryInterface, "create")
    mock_logger = mocker.patch.object(LoggerInterface, "log_info")
    mock_session_repository = mocker.patch.object(SessionRepositoryInterface, "get_current_user")

    mock_validator = mocker.patch("src.interactor.use_cases.create_condition.CreateConditionInputDtoValidator")
    mock_validator_instance = mock_validator.return_value
    mock_presenter.present.return_value = "Test output"
    mock_session_repository.return_value = "Test user"
    mock_condition_repository.create.return_value = condition

    use_case = CreateConditionUseCase(
        mock_presenter,
        mock_condition_repository,
        mock_logger,
        mock_session_repository,
    )

    input_dto = CreateConditionInputDto(
        action=fixture_create_condition["action"],
        trigger_price=fixture_create_condition["trigger_price"],
        turning_point=fixture_create_condition["turning_point"],
        quantity=fixture_create_condition["quantity"],
        take_profit_point=fixture_create_condition["take_profit_point"],
        stop_loss_point=fixture_create_condition["stop_loss_point"],
        is_following=fixture_create_condition["is_following"]
    )
    result = use_case.execute(input_dto)

    mock_validator.assert_called_once_with(input_dto.to_dict())
    mock_validator_instance.validate.assert_called_once_with()

    mock_session_repository.get_current_user.assert_called_once()

    mock_condition_repository.create.assert_called_once_with(
        action=fixture_create_condition["action"],
        trigger_price=fixture_create_condition["trigger_price"],
        turning_point=fixture_create_condition["turning_point"],
        quantity=fixture_create_condition["quantity"],
        take_profit_point=fixture_create_condition["take_profit_point"],
        stop_loss_point=fixture_create_condition["stop_loss_point"],
        is_following=fixture_create_condition["is_following"]
    )

    output_dto = CreateConditionOutputDto(
        condition=mock_condition_repository.create.return_value
    )

    mock_presenter.present.assert_called_once_with(output_dto)
    mock_logger.log_info.assert_called_once_with("Condition created successfully")

    assert result == "Test output"


def test_create_condition_if_user_is_none(mocker, fixture_create_condition):
    mock_presenter = mocker.patch.object(CreateConditionPresenterInterface, "present")
    mock_condition_repository = mocker.patch.object(ConditionRepositoryInterface, "create")
    mock_logger = mocker.patch.object(LoggerInterface, "log_info")
    mock_session_repository = mocker.patch.object(SessionRepositoryInterface, "get_current_user")
    mock_session_repository.get_current_user.return_value = None

    validator_mock = mocker.patch("src.interactor.use_cases.create_condition.CreateConditionInputDtoValidator")
    validator_mock_instance = validator_mock.return_value

    use_case = CreateConditionUseCase(
        mock_presenter,
        mock_condition_repository,
        mock_logger,
        mock_session_repository,
    )
    input_dto = CreateConditionInputDto(
        action=fixture_create_condition["action"],
        trigger_price=fixture_create_condition["trigger_price"],
        turning_point=fixture_create_condition["turning_point"],
        quantity=fixture_create_condition["quantity"],
        take_profit_point=fixture_create_condition["take_profit_point"],
        stop_loss_point=fixture_create_condition["stop_loss_point"],
        is_following=fixture_create_condition["is_following"]
    )

    with pytest.raises(LoginFailedException) as exc:
        use_case.execute(input_dto)

    validator_mock.assert_called_once_with(input_dto.to_dict())
    validator_mock_instance.validate.assert_called_once_with()

    mock_session_repository.get_current_user.assert_called_once()

    assert str(exc.value) == "Login failed: User not logged in"


def test_create_condition_if_creation_failed(mocker, fixture_create_condition):
    mock_presenter = mocker.patch.object(CreateConditionPresenterInterface, "present")
    mock_logger = mocker.patch.object(LoggerInterface, "log_info")
    mock_condition_repository = mocker.patch.object(ConditionRepositoryInterface, "create")
    mock_condition_repository.create.return_value = None
    mock_session_repository = mocker.patch.object(SessionRepositoryInterface, "get_current_user")
    mock_session_repository.get_current_user.return_value = "Test user"

    validator_mock = mocker.patch("src.interactor.use_cases.create_condition.CreateConditionInputDtoValidator")
    validator_mock_instance = validator_mock.return_value
    mock_presenter.present.return_value = "Test output"

    use_case = CreateConditionUseCase(
        mock_presenter,
        mock_condition_repository,
        mock_logger,
        mock_session_repository,
    )
    input_dto = CreateConditionInputDto(
        action=fixture_create_condition["action"],
        trigger_price=fixture_create_condition["trigger_price"],
        turning_point=fixture_create_condition["turning_point"],
        quantity=fixture_create_condition["quantity"],
        take_profit_point=fixture_create_condition["take_profit_point"],
        stop_loss_point=fixture_create_condition["stop_loss_point"],
        is_following=fixture_create_condition["is_following"]
    )

    with pytest.raises(Exception) as exc:
        use_case.execute(input_dto)

    validator_mock.assert_called_once_with(input_dto.to_dict())
    validator_mock_instance.validate.assert_called_once_with()

    mock_session_repository.get_current_user.assert_called_once()

    assert str(exc.value) == f"Condition '{input_dto.to_dict()}' was not created correctly"
