from unittest.mock import MagicMock, patch

from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.user_logout_presenter import UserLogoutPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.use_cases.user_logout import UserLogoutUseCase


def test_user_logout():
    # Create mocks
    presenter_mock = MagicMock(spec=UserLogoutPresenterInterface)
    logger_mock = MagicMock(spec=LoggerInterface)
    session_manager_mock = MagicMock(spec=SessionRepositoryInterface)
    
    # Create service container mock
    service_container_mock = MagicMock()
    service_container_mock.exchange_client.PFCLogout = MagicMock()

    use_case = UserLogoutUseCase(
        presenter_mock,
        service_container_mock,
        logger_mock,
        session_manager_mock
    )

    input_dto = UserLogoutInputDto(account="test_account")
    
    with patch("src.interactor.use_cases.user_logout.UserLogoutInputDtoValidator") as validator_mock:
        result = use_case.execute(input_dto)
        validator_mock.assert_called_once_with(input_dto.to_dict())
        validator_instance = validator_mock.return_value
        validator_instance.validate.assert_called_once_with()

    service_container_mock.exchange_client.PFCLogout.assert_called_once()
    session_manager_mock.destroy_session.assert_called_once()
    logger_mock.log_info.assert_called_once_with("User logout successfully")
    presenter_mock.present.assert_called_once()
    assert result is not None
