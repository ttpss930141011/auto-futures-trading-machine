# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from src.app.cli_pfcf.presenters.user_login_presenter import UserLoginPresenter
from src.domain.entities.user import User
from src.interactor.dtos.user_login_dtos import UserLoginOutputDto


def test_user_login_presenter(fixture_user):
    user = User(
        account=fixture_user["account"],
        password=fixture_user["password"],
        ip_address=fixture_user["ip_address"],
        client=fixture_user["client"]
    )
    output_dto = UserLoginOutputDto(user)
    presenter = UserLoginPresenter()
    assert presenter.present(output_dto) == {
        "action": "user_login",
        "message": "User logged in successfully",
        "account": user.account,
        "ip_address": user.ip_address,
    }
