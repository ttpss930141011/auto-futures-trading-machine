import pytest

from src.app.cli_pfcf.views.create_condition_view import CreateConditionView
from src.app.cli_pfcf.views.select_order_account_view import SelectOrderAccountView
from src.app.cli_pfcf.views.send_market_order_view import SendMarketOrderView


@pytest.mark.parametrize("view_class", [CreateConditionView, SelectOrderAccountView, SendMarketOrderView])
def test_simple_views_print_dict(view_class, capsys):
    data = {'foo': 'bar', 'num': 123}
    view = view_class()
    view.show(data)
    captured = capsys.readouterr()
    # Should print the dict representation
    assert captured.out == str(data) + "\n"
