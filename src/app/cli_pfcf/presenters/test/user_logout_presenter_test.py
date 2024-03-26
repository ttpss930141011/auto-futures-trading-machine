# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from src.app.cli_pfcf.presenters.user_logout_presenter import UserLogoutPresenter
from src.interactor.dtos.user_logout_dtos import UserLogoutOutputDto


def test_user_logout_presenter(fixture_user):
    output_dto = UserLogoutOutputDto(
        account=fixture_user["account"],
        is_success=True
    )
    presenter = UserLogoutPresenter()
    assert presenter.present(output_dto) == {
        "action": "logout",
        "message": f"User logout successfully",
        "account": fixture_user["account"],
        "is_success": True
    }
