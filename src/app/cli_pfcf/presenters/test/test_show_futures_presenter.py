from src.app.cli_pfcf.presenters.show_futures_presenter import ShowFuturesPresenter
from src.interactor.dtos.show_futures_dtos import FutureDataDto


class DummyData:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_present_futures_data_empty():
    presenter = ShowFuturesPresenter()
    output = presenter.present_futures_data([])
    assert output.success is False
    assert output.message == "No futures data found"
    assert output.futures_data is None


def test_present_futures_data_valid():
    presenter = ShowFuturesPresenter()
    data = DummyData(
        COMMODITYID=1,
        desc="Prod",
        month=12,
        Class="Mkt",
        Premium=5,
        MaxPrice=10.5,
        MinPrice=1.2,
    )
    output = presenter.present_futures_data([data])
    assert output.success is True
    assert output.message == "Found 1 futures items"
    assert isinstance(output.futures_data, list)
    assert len(output.futures_data) == 1
    f = output.futures_data[0]
    assert isinstance(f, FutureDataDto)
    assert f.commodity_id == "1"
    assert f.product_name == "Prod"
    assert f.underlying_id == ""
    assert f.delivery_month == "12"
    assert f.market_code == "Mkt"
    assert f.position_price == "5"
    assert f.expiration_date == ""
    assert f.max_price == 10.5
    assert f.min_price == 1.2


def test_present_futures_data_invalid_entries():
    presenter = ShowFuturesPresenter()
    bad = DummyData()  # missing attributes
    good = DummyData(
        COMMODITYID="C",
        desc="D",
        month="M",
        Class="C",
        Premium="",
        MaxPrice=None,
        MinPrice=0,
    )
    output = presenter.present_futures_data([bad, good])
    # bad entry is skipped, good one processed
    assert output.success is True
    assert len(output.futures_data) == 1


def test_present_error():
    presenter = ShowFuturesPresenter()
    output = presenter.present_error("oops")
    assert output.success is False
    assert output.message == "Error: oops"
    assert output.futures_data is None
