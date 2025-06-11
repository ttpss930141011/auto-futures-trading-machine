# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


import pytest
from unittest.mock import MagicMock, patch

from src.domain.entities.user import User
from src.interactor.dtos.user_login_dtos import UserLoginInputDto, UserLoginOutputDto
from src.interactor.errors.error_classes import ItemNotCreatedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.user_login_presenter import UserLoginPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.interfaces.repositories.user_repository import UserRepositoryInterface
from src.interactor.use_cases import user_login


def test_user_login(fixture_user):
    user = User(
        fixture_user["account"],
        fixture_user["password"],
        fixture_user["ip_address"],
        fixture_user["client"]
    )
    # Create mocks
    presenter_mock = MagicMock(spec=UserLoginPresenterInterface)
    repository_mock = MagicMock(spec=UserRepositoryInterface)
    logger_mock = MagicMock(spec=LoggerInterface)
    session_manager_mock = MagicMock(spec=SessionRepositoryInterface)
    
    # Create service container mock
    service_container_mock = MagicMock()
    service_container_mock.exchange_client.PFCLogin = MagicMock()
    
    repository_mock.get.return_value = None
    repository_mock.create.return_value = user
    presenter_mock.present.return_value = "Test output"
    
    use_case = user_login.UserLoginUseCase(
        presenter_mock,
        repository_mock,
        service_container_mock,
        logger_mock,
        session_manager_mock
    )
    input_dto = UserLoginInputDto(
        account=fixture_user["account"],
        password=fixture_user["password"],
        ip_address=fixture_user["ip_address"]
    )
    
    with patch("src.interactor.use_cases.user_login.UserLoginInputDtoValidator") as input_dto_validator_mock:
        result = use_case.execute(input_dto)
        input_dto_validator_mock.assert_called_once_with(input_dto.to_dict())
        input_dto_validator_instance = input_dto_validator_mock.return_value
        input_dto_validator_instance.validate.assert_called_once_with()
    
    service_container_mock.exchange_client.PFCLogin.assert_called_once_with(
        fixture_user["account"],
        fixture_user["password"],
        fixture_user["ip_address"]
    )
    repository_mock.get.assert_called_once()
    session_manager_mock.create_session.assert_called_once_with(account=fixture_user["account"])
    logger_mock.log_info.assert_called_once_with("User login successfully")
    output_dto = UserLoginOutputDto(user)
    presenter_mock.present.assert_called_once_with(output_dto)
    assert result == "Test output"

    # Testing None return value from repository
    repository_mock.create.return_value = None
    user_account = fixture_user["account"]
    with pytest.raises(ItemNotCreatedException) as exception_info:
        use_case.execute(input_dto)
    assert str(exception_info.value) == f"User '{user_account}' was not created correctly"


def test_user_login_empty_field(fixture_user):
    # Create mocks
    presenter_mock = MagicMock(spec=UserLoginPresenterInterface)
    repository_mock = MagicMock(spec=UserRepositoryInterface)
    logger_mock = MagicMock(spec=LoggerInterface)
    session_manager_mock = MagicMock(spec=SessionRepositoryInterface)
    service_container_mock = MagicMock()

    use_case = user_login.UserLoginUseCase(
        presenter_mock,
        repository_mock,
        service_container_mock,
        logger_mock,
        session_manager_mock
    )
    input_dto = UserLoginInputDto(
        account="",
        password=fixture_user["password"],
        ip_address=fixture_user["ip_address"]
    )
    with pytest.raises(ValueError) as exception_info:
        use_case.execute(input_dto)
    assert str(exception_info.value) == "Account: empty values not allowed"

    repository_mock.create.assert_not_called()
    presenter_mock.present.assert_not_called()
