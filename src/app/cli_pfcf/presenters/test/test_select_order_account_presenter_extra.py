import pytest

from src.app.cli_pfcf.presenters.select_order_account_presenter import SelectOrderAccountPresenter
from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountOutputDto


def test_select_order_account_presenter():
    dto = SelectOrderAccountOutputDto(order_account="ACC123")
    presenter = SelectOrderAccountPresenter()
    result = presenter.present(dto)
    assert isinstance(result, dict)
    assert result["action"] == "select_order_account"
    assert "Order account selected: ACC123" == result["message"]

@pytest.mark.parametrize("account", ["X", "", None])
def test_select_order_account_presenter_empty(account):
    # Even empty or None account is formatted in message
    dto = SelectOrderAccountOutputDto(order_account=account)
    presenter = SelectOrderAccountPresenter()
    result = presenter.present(dto)
    assert result["action"] == "select_order_account"
    assert f"Order account selected: {account}" == result["message"]