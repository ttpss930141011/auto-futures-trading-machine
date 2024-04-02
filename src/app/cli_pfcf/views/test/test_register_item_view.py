# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.app.cli_pfcf.views.register_item_view import RegisterItemView


def test_register_item_view(capsys):
    response = {'action': 'register_item', 'message': 'User registered successfully'}
    view = RegisterItemView()
    view.show(response)
    captured = capsys.readouterr()
    assert captured.out == str(response) + "\n"
