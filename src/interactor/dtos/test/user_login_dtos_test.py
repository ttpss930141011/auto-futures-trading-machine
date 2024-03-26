# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from src.interactor.dtos.user_login_dtos import UserLoginInputDto


def test_user_login_input_dto_valid(fixture_user):
    input_dto = UserLoginInputDto(
        account=fixture_user["account"],
        password=fixture_user["password"],
        ip_address=fixture_user["ip_address"]
    )
    assert input_dto.account == fixture_user["account"]
    assert input_dto.password == fixture_user["password"]
    assert input_dto.ip_address == fixture_user["ip_address"]
    assert input_dto.to_dict() == {
        "account": fixture_user["account"],
        "password": fixture_user["password"],
        "ip_address": fixture_user["ip_address"]
    }
