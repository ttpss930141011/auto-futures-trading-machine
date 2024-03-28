# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from src.app.cli_pfcf.presenters.register_item_presenter import RegisterItemPresenter
from src.interactor.dtos.register_item_dtos import RegisterItemOutputDto


def test_register_item_presenter(fixture_register_item):
    output_dto = RegisterItemOutputDto(
        account=fixture_register_item["account"],
        item_code=fixture_register_item["item_code"],
        is_registered=True,
    )
    presenter = RegisterItemPresenter()
    assert presenter.present(output_dto) == {
        "action": "register_item",
        "message": "User registered successfully",
    }
