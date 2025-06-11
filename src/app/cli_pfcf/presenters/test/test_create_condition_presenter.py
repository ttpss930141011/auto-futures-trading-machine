import uuid

import pytest
from src.app.cli_pfcf.presenters.create_condition_presenter import CreateConditionPresenter
from src.interactor.dtos.create_condition_dtos import CreateConditionOutputDto
from src.domain.entities.condition import Condition
from src.domain.value_objects import OrderOperation


def test_create_condition_presenter_buy():
    cid = uuid.uuid4()
    cond = Condition(condition_id=cid, action=OrderOperation.BUY, trigger_price=100, quantity=5)
    dto = CreateConditionOutputDto(condition=cond)
    presenter = CreateConditionPresenter()
    result = presenter.present(dto)
    assert result["action"] == "create_condition"
    assert f"Condition {cid}" in result["message"]
    assert result["condition"] == cond.to_dict()


def test_create_condition_presenter_sell():
    cid = uuid.uuid4()
    cond = Condition(condition_id=cid, action=OrderOperation.SELL, trigger_price=200, quantity=3)
    dto = CreateConditionOutputDto(condition=cond)
    presenter = CreateConditionPresenter()
    result = presenter.present(dto)
    assert result["action"] == "create_condition"
    assert f"Condition {cid}" in result["message"]
    assert result["condition"]["order_price"] == cond.order_price
