# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.interactor.dtos.register_item_dtos import RegisterItemInputDto


def test_register_item_input_dto_valid(fixture_register_item):
    input_dto = RegisterItemInputDto(
        account=fixture_register_item["account"],
        item_code=fixture_register_item["item_code"],
    )

    assert input_dto.account == fixture_register_item["account"]
    assert input_dto.item_code == fixture_register_item["item_code"]
    assert input_dto.to_dict() == {
        "account": fixture_register_item["account"],
        "item_code": fixture_register_item["item_code"],
    }
