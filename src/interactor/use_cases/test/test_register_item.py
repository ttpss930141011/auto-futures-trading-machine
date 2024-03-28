import pytest

from src.interactor.dtos.register_item_dtos import RegisterItemInputDto, RegisterItemOutputDto
from src.interactor.errors.error_classes import LoginFailedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.register_item_presenter import RegisterItemPresenterInterface
from src.interactor.interfaces.session_manager.session_manager import SessionManagerInterface
from src.interactor.use_cases.register_item import RegisterItemUseCase


class Item:
    def __init__(self, commodity_id):
        self.COMMODITYID = commodity_id


def test_register_item(mocker, fixture_register_item):
    presenter_mock = mocker.patch.object(RegisterItemPresenterInterface, "present")
    config_mock = mocker.patch("src.app.cli_pfcf.config.Config")
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    session_manager_mock = mocker.patch.object(SessionManagerInterface, "get_current_user")
    event_handler_mock = mocker.MagicMock()

    validator_mock = mocker.patch("src.interactor.use_cases.register_item.RegisterItemInputDtoValidator")
    validator_mock_instance = validator_mock.return_value
    presenter_mock.present.return_value = "Test output"
    session_manager_mock.return_value = "Test user"
    config_mock.DEALER_CLIENT.DQuoteLib.RegItem = mocker.MagicMock()
    config_mock.DEALER_CLIENT.DQuoteLib.OnTickDataTrade = mocker.MagicMock()
    config_mock.DEALER_CLIENT.PFCGetFutureData = mocker.MagicMock()

    # Mock data for items_object_list
    items_object_list = [Item(fixture_register_item["item_code"]), Item("COM5678")]
    config_mock.DEALER_CLIENT.PFCGetFutureData.return_value = items_object_list

    use_case = RegisterItemUseCase(
        presenter_mock,
        config_mock,
        logger_mock,
        session_manager_mock,
        event_handler_mock
    )
    input_dto = RegisterItemInputDto(
        account=fixture_register_item["account"],
        item_code=fixture_register_item["item_code"]
    )
    result = use_case.execute(input_dto)

    validator_mock.assert_called_once_with(input_dto.to_dict())
    validator_mock_instance.validate.assert_called_once_with()

    session_manager_mock.get_current_user.assert_called_once()

    config_mock.DEALER_CLIENT.DQuoteLib.RegItem.assert_called_once_with(fixture_register_item["item_code"])

    output_dto = RegisterItemOutputDto(
        account=fixture_register_item["account"],
        item_code=fixture_register_item["item_code"],
        is_registered=True
    )

    presenter_mock.present.assert_called_once_with(output_dto)
    logger_mock.log_info.assert_called_once_with(
        f"Account {fixture_register_item['account']} register item {fixture_register_item['item_code']} successfully")

    assert result == "Test output"


def test_register_item_if_user_is_none(mocker, fixture_register_item):
    presenter_mock = mocker.patch.object(RegisterItemPresenterInterface, "present")
    config_mock = mocker.patch("src.app.cli_pfcf.config.Config")
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    session_manager_mock = mocker.patch.object(SessionManagerInterface, "get_current_user")
    session_manager_mock.get_current_user.return_value = None
    event_handler_mock = mocker.MagicMock()

    validator_mock = mocker.patch("src.interactor.use_cases.register_item.RegisterItemInputDtoValidator")
    validator_mock_instance = validator_mock.return_value

    use_case = RegisterItemUseCase(
        presenter_mock,
        config_mock,
        logger_mock,
        session_manager_mock,
        event_handler_mock
    )
    input_dto = RegisterItemInputDto(
        account=fixture_register_item["account"],
        item_code=fixture_register_item["item_code"]
    )

    with pytest.raises(LoginFailedException) as exc:
        use_case.execute(input_dto)

    validator_mock.assert_called_once_with(input_dto.to_dict())
    validator_mock_instance.validate.assert_called_once_with()

    session_manager_mock.get_current_user.assert_called_once()
    logger_mock.log_info.assert_called_once_with(f"Login failed: Account {fixture_register_item['account']} not login")

    assert str(exc.value) == f"Login failed: Account {fixture_register_item['account']} not login"


def test_register_item_if_item_code_not_in_items_list(mocker, fixture_register_item):
    presenter_mock = mocker.patch.object(RegisterItemPresenterInterface, "present")
    config_mock = mocker.patch("src.app.cli_pfcf.config.Config")
    logger_mock = mocker.patch.object(LoggerInterface, "log_info")
    session_manager_mock = mocker.patch.object(SessionManagerInterface, "get_current_user")
    session_manager_mock.get_current_user.return_value = "Test user"
    event_handler_mock = mocker.MagicMock()

    validator_mock = mocker.patch("src.interactor.use_cases.register_item.RegisterItemInputDtoValidator")
    validator_mock_instance = validator_mock.return_value
    presenter_mock.present.return_value = "Test output"
    config_mock.DEALER_CLIENT.DQuoteLib.RegItem = mocker.MagicMock()
    config_mock.DEALER_CLIENT.DQuoteLib.OnTickDataTrade = mocker.MagicMock()
    config_mock.DEALER_CLIENT.PFCGetFutureData = mocker.MagicMock()

    # Mock data for items_object_list
    items_object_list = [Item("COM1234"), Item("COM5678")]
    config_mock.DEALER_CLIENT.PFCGetFutureData.return_value = items_object_list

    use_case = RegisterItemUseCase(
        presenter_mock,
        config_mock,
        logger_mock,
        session_manager_mock,
        event_handler_mock
    )
    input_dto = RegisterItemInputDto(
        account=fixture_register_item["account"],
        item_code=fixture_register_item["item_code"]
    )

    with pytest.raises(Exception) as exc:
        use_case.execute(input_dto)

    validator_mock.assert_called_once_with(input_dto.to_dict())
    validator_mock_instance.validate.assert_called_once_with()

    session_manager_mock.get_current_user.assert_called_once()

    logger_mock.log_info.assert_called_once_with(f"Item not found: {fixture_register_item['item_code']} is not found")

    assert str(exc.value) == f"Item not found: {fixture_register_item['item_code']} is not found"
