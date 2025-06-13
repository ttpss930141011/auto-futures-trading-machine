import pytest

from src.app.cli_pfcf.presenters.send_market_order_presenter import SendMarketOrderPresenter
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderOutputDto


@pytest.mark.parametrize("is_send, note, serial", [
    (True, "Order sent successfully", "ABC123"),
    (False, "Order failed", "XYZ789"),
])
def test_send_market_order_presenter(is_send, note, serial):
    dto = SendMarketOrderOutputDto(is_send_order=is_send, note=note, order_serial=serial)
    presenter = SendMarketOrderPresenter()
    result = presenter.present(dto)
    assert isinstance(result, dict)
    assert result["action"] == "send_market_order"
    assert serial in result["message"]
    assert result["note"] == note
    assert result["order_serial"] == serial
