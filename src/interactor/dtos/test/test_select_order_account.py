# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.interactor.dtos.select_order_account_dtos import SelectOrderAccountInputDto


def test_select_order_account_input_dto_valid(fixture_select_order_account):
    input_dto = SelectOrderAccountInputDto(
        index=fixture_select_order_account["index"],
        order_account=fixture_select_order_account["order_account"],
    )

    assert input_dto.index == fixture_select_order_account["index"]
    assert input_dto.order_account == fixture_select_order_account["order_account"]
    assert input_dto.to_dict() == {
        "index": fixture_select_order_account["index"],
        "order_account": fixture_select_order_account["order_account"],
    }
