from src.app.cli_pfcf.views.show_futures_view import ShowFuturesView
from src.interactor.dtos.show_futures_dtos import FutureDataDto, ShowFuturesOutputDto


def test_show_no_futures_data(capsys):
    view = ShowFuturesView()
    output_dto = ShowFuturesOutputDto(success=False, message="No data found", futures_data=None)
    view.show(output_dto)
    captured = capsys.readouterr()
    # Should print only the message
    assert "No data found" in captured.out
    assert "==== Futures Data" not in captured.out


def test_show_empty_futures_list(capsys):
    view = ShowFuturesView()
    output_dto = ShowFuturesOutputDto(success=True, message="No valid futures data found", futures_data=[])
    view.show(output_dto)
    captured = capsys.readouterr()
    assert "No valid futures data found" in captured.out
    assert "==== Futures Data" not in captured.out


def test_show_futures_data(capsys):
    view = ShowFuturesView()
    f1 = FutureDataDto(
        commodity_id='ID1', product_name='Prod1', underlying_id='U1',
        delivery_month='M1', market_code='C1', position_price='10', expiration_date='E1'
    )
    f2 = FutureDataDto(
        commodity_id='ID2', product_name='Prod2', underlying_id='U2',
        delivery_month='M2', market_code='C2', position_price='20', expiration_date='E2'
    )
    output_dto = ShowFuturesOutputDto(
        success=True,
        message="Found 2 futures items",
        futures_data=[f1, f2]
    )
    view.show(output_dto)
    out = capsys.readouterr().out
    # Check message and table header
    assert "Found 2 futures items" in out
    assert "==== Futures Data ====" in out
    # Check header labels
    assert '商品代號' in out and '商品名稱' in out
    # Check data rows and total
    assert 'ID1' in out and 'Prod1' in out
    assert 'ID2' in out and 'Prod2' in out
    assert 'Total items: 2' in out
