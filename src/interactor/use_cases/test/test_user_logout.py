from unittest.mock import MagicMock, patch

from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto
from src.interactor.interfaces.presenters.user_logout_presenter import UserLogoutPresenterInterface
from src.interactor.use_cases.user_logout import UserLogoutUseCase


def test_user_logout():
    presenter_mock = MagicMock(spec=UserLogoutPresenterInterface)
    service_container_mock = MagicMock()

    use_case = UserLogoutUseCase(presenter_mock, service_container_mock)
    input_dto = UserLogoutInputDto(account="test_account")

    with patch("src.interactor.use_cases.user_logout.UserLogoutInputDtoValidator") as validator_mock:
        result = use_case.execute(input_dto)
        validator_mock.assert_called_once_with(input_dto.to_dict())
        validator_mock.return_value.validate.assert_called_once_with()

    service_container_mock.exchange_api.client.PFCLogout.assert_called_once()
    service_container_mock.session_repository.destroy_session.assert_called_once()
    service_container_mock.logger.log_info.assert_called_once_with("User logout successfully")
    presenter_mock.present.assert_called_once()
    assert result is not None
