# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.app.cli_pfcf.views.on_tick_data_trade_view import OnTickDataTradeView


def test_register_item_view(capsys):
    response = {'action': 'register_item', 'message': 'User registered successfully'}
    view = OnTickDataTradeView()
    view.show(response)
    captured = capsys.readouterr()
    assert captured.out == str(response) + "\n"
