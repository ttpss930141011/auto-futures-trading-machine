from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.user_logout_presenter import UserLogoutPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.use_cases.user_logout import UserLogoutUseCase


def test_user_logout(mocker):
    presenter_mock = mocker.patch.object(UserLogoutPresenterInterface, "present")
    config_mock = mocker.patch("src.app.cli_pfcf.config.Config")
    config_mock.DEALER_CLIENT.PFCLogout = mocker.MagicMock()
    session_manager_mock = mocker.patch.object(SessionRepositoryInterface, "destroy_session")
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    validator_mock = mocker.patch("src.interactor.use_cases.user_logout.UserLogoutInputDtoValidator")

    use_case = UserLogoutUseCase(
        presenter_mock,
        config_mock,
        logger_mock,
        session_manager_mock
    )

    input_dto = UserLogoutInputDto(account="test_account")
    result = use_case.execute(input_dto)

    validator_mock.assert_called_once_with(input_dto.to_dict())
    validator_instance = validator_mock.return_value
    validator_instance.validate.assert_called_once_with()

    config_mock.DEALER_CLIENT.PFCLogout.assert_called_once()

    config_mock.DEALER_CLIENT.PFCLogout.assert_called_once()
    session_manager_mock.destroy_session.assert_called_once()
    logger_mock.log_info.assert_called_once_with("User logout successfully")
    presenter_mock.present.assert_called_once()
    assert result is not None
