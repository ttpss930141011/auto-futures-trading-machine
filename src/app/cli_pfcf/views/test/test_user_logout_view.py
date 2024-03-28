# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from src.app.cli_pfcf.views.user_logout_view import UserLogoutView


def test_user_logout_view(capsys, fixture_user):
    user_dict = {
        "account": fixture_user["account"],
        "password": fixture_user["password"],
        "ip_address": fixture_user["ip_address"],
        "client": fixture_user["client"]
    }
    view = UserLogoutView()
    view.show(user_dict)
    captured = capsys.readouterr()
    assert captured.out == str(user_dict) + "\n"
