import pytest
from unittest.mock import MagicMock, patch

from src.interactor.dtos.register_item_dtos import RegisterItemInputDto, RegisterItemOutputDto
from src.interactor.errors.error_classes import LoginFailedException
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.register_item_presenter import RegisterItemPresenterInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.use_cases.register_item import RegisterItemUseCase


class Item:
    def __init__(self, commodity_id):
        self.COMMODITYID = commodity_id


def test_register_item(fixture_register_item):
    presenter_mock = MagicMock(spec=RegisterItemPresenterInterface)
    service_container_mock = MagicMock()
    logger_mock = MagicMock(spec=LoggerInterface)
    session_manager_mock = MagicMock(spec=SessionRepositoryInterface)

    # Set up service container attributes
    service_container_mock.logger = logger_mock
    service_container_mock.session_repository = session_manager_mock

    with patch("src.interactor.use_cases.register_item.RegisterItemInputDtoValidator") as validator_mock:
        validator_mock_instance = validator_mock.return_value
        presenter_mock.present.return_value = "Test output"
        session_manager_mock.get_current_user.return_value = "Test user"
        service_container_mock.exchange_client.DQuoteLib.RegItem = MagicMock()
        service_container_mock.exchange_client.DQuoteLib.OnTickDataTrade = MagicMock()
        service_container_mock.exchange_client.PFCGetFutureData = MagicMock()

        # Mock data for items_object_list
        items_object_list = [Item(fixture_register_item["item_code"]), Item("COM5678")]
        service_container_mock.exchange_client.PFCGetFutureData.return_value = items_object_list

        use_case = RegisterItemUseCase(
            presenter_mock,
            service_container_mock,
        )
        input_dto = RegisterItemInputDto(
            account=fixture_register_item["account"],
            item_code=fixture_register_item["item_code"]
        )
        result = use_case.execute(input_dto)

        validator_mock.assert_called_once_with(input_dto.to_dict())
        validator_mock_instance.validate.assert_called_once_with()

        session_manager_mock.get_current_user.assert_called_once()

        service_container_mock.exchange_client.DQuoteLib.RegItem.assert_called_once_with(fixture_register_item["item_code"])

        output_dto = RegisterItemOutputDto(
            account=fixture_register_item["account"],
            item_code=fixture_register_item["item_code"],
            is_registered=True
        )

        presenter_mock.present.assert_called_once_with(output_dto)
        logger_mock.log_info.assert_called_once_with(
            f"Account {fixture_register_item['account']} register item {fixture_register_item['item_code']} successfully")

        assert result == "Test output"


def test_register_item_if_user_is_none(fixture_register_item):
    presenter_mock = MagicMock(spec=RegisterItemPresenterInterface)
    service_container_mock = MagicMock()
    logger_mock = MagicMock(spec=LoggerInterface)
    session_manager_mock = MagicMock(spec=SessionRepositoryInterface)

    # Set up service container attributes
    service_container_mock.logger = logger_mock
    service_container_mock.session_repository = session_manager_mock
    session_manager_mock.get_current_user.return_value = None

    with patch("src.interactor.use_cases.register_item.RegisterItemInputDtoValidator") as validator_mock:
        validator_mock_instance = validator_mock.return_value

        use_case = RegisterItemUseCase(
            presenter_mock,
            service_container_mock,
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

        assert str(exc.value) == f"Login failed: Account {fixture_register_item['account']} not login"


def test_register_item_if_item_code_not_in_items_list(fixture_register_item):
    presenter_mock = MagicMock(spec=RegisterItemPresenterInterface)
    service_container_mock = MagicMock()
    logger_mock = MagicMock(spec=LoggerInterface)
    session_manager_mock = MagicMock(spec=SessionRepositoryInterface)

    # Set up service container attributes
    service_container_mock.logger = logger_mock
    service_container_mock.session_repository = session_manager_mock
    session_manager_mock.get_current_user.return_value = "Test user"

    with patch("src.interactor.use_cases.register_item.RegisterItemInputDtoValidator") as validator_mock:
        validator_mock_instance = validator_mock.return_value
        presenter_mock.present.return_value = "Test output"
        service_container_mock.exchange_client.DQuoteLib.RegItem = MagicMock()
        service_container_mock.exchange_client.DQuoteLib.OnTickDataTrade = MagicMock()
        service_container_mock.exchange_client.PFCGetFutureData = MagicMock()

        # Mock data for items_object_list
        items_object_list = [Item("COM1234"), Item("COM5678")]
        service_container_mock.exchange_client.PFCGetFutureData.return_value = items_object_list

        use_case = RegisterItemUseCase(
            presenter_mock,
            service_container_mock,
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

        assert str(exc.value) == f"Item not found: {fixture_register_item['item_code']} is not found"
