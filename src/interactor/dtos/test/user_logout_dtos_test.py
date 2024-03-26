# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from src.interactor.dtos.user_logout_dtos import UserLogoutInputDto


def test_user_login_input_dto_valid(fixture_user):
    input_dto = UserLogoutInputDto(
        account=fixture_user["account"],
    )
    assert input_dto.account == fixture_user["account"]
    assert input_dto.to_dict() == {
        "account": fixture_user["account"],
    }
