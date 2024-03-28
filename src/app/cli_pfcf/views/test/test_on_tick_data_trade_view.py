# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.app.cli_pfcf.views.on_tick_data_trade_view import OnTickDataTradeView


def test_on_tick_data_trade_view(capsys, fixture_tick_data_trade):
    data = {'commodity_id': fixture_tick_data_trade['commodity_id'],
            'info_time': fixture_tick_data_trade['info_time'],
            'match_time': fixture_tick_data_trade['match_time'],
            'match_price': fixture_tick_data_trade['match_price'],
            'match_buy_cnt': fixture_tick_data_trade['match_buy_cnt'],
            'match_sell_cnt': fixture_tick_data_trade['match_sell_cnt'],
            'match_quantity': fixture_tick_data_trade['match_quantity'],
            'match_total_qty': fixture_tick_data_trade['match_total_qty']
            }
    view = OnTickDataTradeView()
    view.show(data)
    captured = capsys.readouterr()
    assert captured.out == str(data) + "\n"
