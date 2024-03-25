# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


import pytest

from src.domain.entities.user import User
from src.interactor.dtos.user_login_dtos \
    import UserLoginInputDto, UserLoginOutputDto
from src.interactor.errors.error_classes import ItemNotCreatedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.user_login_presenter \
    import UserLoginPresenterInterface
from src.interactor.interfaces.repositories.user_repository \
    import UserRepositoryInterface
from src.interactor.interfaces.session_manager.session_manager import SessionManagerInterface
from src.interactor.use_cases import user_login


def test_user_login(mocker, fixture_user):
    user = User(
        fixture_user["account"],
        fixture_user["password"],
        fixture_user["ip_address"],
        fixture_user["client"]
    )
    presenter_mock = mocker.patch.object(UserLoginPresenterInterface, "present")
    repository_mock = mocker.patch.object(UserRepositoryInterface, "create")
    config_mock = mocker.patch("src.app.cli_pfcf.config.Config")
    config_mock.DEALER_CLIENT.PFCLogin = mocker.MagicMock()
    session_manager_mock = mocker.patch.object(SessionManagerInterface, "create_session")

    input_dto_validator_mock = mocker.patch("src.interactor.use_cases.user_login.UserLoginInputDtoValidator")
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    repository_mock.get.return_value = None
    repository_mock.create.return_value = user
    presenter_mock.present.return_value = "Test output"
    use_case = user_login.UserLoginUseCase(
        presenter_mock,
        repository_mock,
        config_mock,
        logger_mock,
        session_manager_mock
    )
    input_dto = UserLoginInputDto(
        account=fixture_user["account"],
        password=fixture_user["password"],
        ip_address=fixture_user["ip_address"]
    )
    result = use_case.execute(input_dto)
    input_dto_validator_mock.assert_called_once_with(input_dto.to_dict())
    input_dto_validator_instance = input_dto_validator_mock.return_value
    input_dto_validator_instance.validate.assert_called_once_with()
    config_mock.DEALER_CLIENT.PFCLogin.assert_called_once_with(
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
    print(f"User account: {user_account}")
    with pytest.raises(ItemNotCreatedException) as exception_info:
        use_case.execute(input_dto)
    assert str(exception_info.value) == f"User '{user_account}' was not created correctly"


def test_user_login_empty_field(mocker, fixture_user):
    presenter_mock = mocker.patch.object(UserLoginPresenterInterface, "present")
    repository_mock = mocker.patch.object(UserRepositoryInterface, "create")
    config_mock = mocker.patch("src.app.cli_pfcf.config.Config")
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    session_manager_mock = mocker.patch.object(SessionManagerInterface, "create_session")

    use_case = user_login.UserLoginUseCase(
        presenter_mock,
        repository_mock,
        config_mock,
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
