import pytest

from src.interactor.dtos.send_market_order_dtos import (
    SendMarketOrderInputDto,
    SendMarketOrderOutputDto,
)
from src.interactor.errors.error_classes import (
    LoginFailedException,
    ItemNotCreatedException,
    SendMarketOrderFailedException,
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.send_market_order_presenter import (
    SendMarketOrderPresenterInterface,
)
from src.interactor.use_cases.send_market_order import SendMarketOrderUseCase


def test_send_market_order(mocker, fixture_send_market_order):
    fake_pfcf_dict = {
        "ACTNO": "12345678900",
        "PRODUCTID": "1234567890",
        "BS": "BUY",
        "ORDERTYPE": "MARKET",
        "PRICE": 100,
        "ORDERQTY": 10,
        "TIMEINFORCE": "IOC",
        "OPENCLOSE": "OPEN",
        "DTRADE": "NO",
        "NOTE": "Test note",
    }

    # mock all dependencies in the use case
    mock_presenter = mocker.patch.object(SendMarketOrderPresenterInterface, "present")
    mock_config = mocker.patch("src.app.cli_pfcf.config.Config")
    mock_config.EXCHANGE_CLIENT.DTradeLib.Order = mocker.MagicMock()

    mock_order_result = mocker.MagicMock()
    mock_order_result.SEQ = "Test order serial"
    mock_order_result.ERRORCODE = ""
    mock_order_result.ERRORMSG = ""
    mock_order_result.ISSEND = True
    mock_order_result.NOTE = fixture_send_market_order["note"]

    mock_config.EXCHANGE_CLIENT.DTradeLib.Order.return_value = mock_order_result

    mock_order_obejct = mocker.MagicMock()
    mock_order_obejct.ACTNO = ""
    mock_order_obejct.PRODUCTID = ""
    mock_order_obejct.BS = ""
    mock_order_obejct.ORDERTYPE = ""
    mock_order_obejct.PRICE = 0
    mock_order_obejct.ORDERQTY = 0
    mock_order_obejct.TIMEINFORCE = ""
    mock_order_obejct.OPENCLOSE = ""
    mock_order_obejct.DTRADE = ""
    mock_order_obejct.NOTE = ""

    mock_config.EXCHANGE_TRADE.OrderObject = mocker.MagicMock()
    mock_config.EXCHANGE_TRADE.OrderObject.return_value = mock_order_obejct
    mock_logger = mocker.patch.object(LoggerInterface, "log_info")
    mock_session_repository = mocker.patch(
        "src.infrastructure.repositories.session_in_memory_repository.SessionInMemoryRepository"
    )
    mock_session_repository.get_current_user.return_value = "Test user"

    mock_validator = mocker.patch(
        "src.interactor.use_cases.send_market_order.SendMarketOrderInputDtoValidator"
    )
    mock_validator_instance = mock_validator.return_value
    mock_presenter.present.return_value = "Test output"
    mock_session_repository.return_value = "Test user"

    use_case = SendMarketOrderUseCase(
        mock_presenter,
        mock_config,
        mock_logger,
        mock_session_repository,
    )

    input_dto = SendMarketOrderInputDto(**fixture_send_market_order)
    input_dto.to_pfcf_dict = mocker.MagicMock()
    input_dto.to_pfcf_dict.return_value = fake_pfcf_dict
    result = use_case.execute(input_dto)

    mock_validator.assert_called_once_with(input_dto.to_dict())
    mock_validator_instance.validate.assert_called_once_with()

    input_dto.to_pfcf_dict.assert_called_once_with(mock_config)

    mock_session_repository.get_current_user.assert_called_once()

    mock_config.EXCHANGE_TRADE.OrderObject.assert_called_once()
    mock_config.EXCHANGE_CLIENT.DTradeLib.Order.assert_called_once()

    output_dto = SendMarketOrderOutputDto(
        is_send_order=True,
        note=input_dto.note,
        order_serial="Test order serial",
        error_code="",
        error_message="",
    )

    mock_presenter.present.assert_called_once_with(output_dto)
    mock_logger.log_info.assert_called_once_with("Order sent successfully")

    assert result == "Test output"


def test_send_market_order_if_user_is_none(mocker, fixture_send_market_order):
    # mock all dependencies in the use case
    mock_presenter = mocker.patch.object(SendMarketOrderPresenterInterface, "present")
    mock_config = mocker.patch("src.app.cli_pfcf.config.Config")
    mock_logger = mocker.patch.object(LoggerInterface, "log_info")
    mock_session_repository = mocker.patch(
        "src.infrastructure.repositories.session_in_memory_repository.SessionInMemoryRepository"
    )
    mock_session_repository.get_current_user.return_value = None

    mock_validator = mocker.patch(
        "src.interactor.use_cases.send_market_order.SendMarketOrderInputDtoValidator"
    )
    mock_validator_instance = mock_validator.return_value

    use_case = SendMarketOrderUseCase(
        mock_presenter,
        mock_config,
        mock_logger,
        mock_session_repository,
    )

    input_dto = SendMarketOrderInputDto(**fixture_send_market_order)
    input_dto.to_pfcf_dict = mocker.MagicMock()

    with pytest.raises(LoginFailedException) as exc:
        use_case.execute(input_dto)

    mock_validator.assert_called_once_with(input_dto.to_dict())
    mock_validator_instance.validate.assert_called_once_with()
    mock_session_repository.get_current_user.assert_called_once()

    mock_presenter.present.assert_not_called()
    mock_logger.log_info.assert_not_called()
    input_dto.to_pfcf_dict.assert_not_called()

    assert str(exc.value) == "Login failed: User not logged in"


def test_send_market_order_if_order_result_is_none(mocker, fixture_send_market_order):
    fake_pfcf_dict = {
        "ACTNO": "12345678900",
        "PRODUCTID": "1234567890",
        "BS": "BUY",
        "ORDERTYPE": "MARKET",
        "PRICE": 100,
        "ORDERQTY": 10,
        "TIMEINFORCE": "IOC",
        "OPENCLOSE": "OPEN",
        "DTRADE": "NO",
        "NOTE": "Test note",
    }

    # mock all dependencies in the use case
    mock_presenter = mocker.patch.object(SendMarketOrderPresenterInterface, "present")
    mock_config = mocker.patch("src.app.cli_pfcf.config.Config")
    mock_config.EXCHANGE_CLIENT.DTradeLib.Order = mocker.MagicMock()

    mock_order_result = None

    mock_config.EXCHANGE_CLIENT.DTradeLib.Order.return_value = mock_order_result

    mock_order_obejct = mocker.MagicMock()
    mock_order_obejct.ACTNO = ""
    mock_order_obejct.PRODUCTID = ""
    mock_order_obejct.BS = ""
    mock_order_obejct.ORDERTYPE = ""
    mock_order_obejct.PRICE = 0
    mock_order_obejct.ORDERQTY = 0
    mock_order_obejct.TIMEINFORCE = ""
    mock_order_obejct.OPENCLOSE = ""
    mock_order_obejct.DTRADE = ""
    mock_order_obejct.NOTE = ""

    mock_config.EXCHANGE_TRADE.OrderObject = mocker.MagicMock()
    mock_config.EXCHANGE_TRADE.OrderObject.return_value = mock_order_obejct
    mock_logger = mocker.patch.object(LoggerInterface, "log_info")
    mock_session_repository = mocker.patch(
        "src.infrastructure.repositories.session_in_memory_repository.SessionInMemoryRepository"
    )
    mock_session_repository.get_current_user.return_value = "Test user"

    mock_validator = mocker.patch(
        "src.interactor.use_cases.send_market_order.SendMarketOrderInputDtoValidator"
    )
    mock_validator_instance = mock_validator.return_value
    mock_presenter.present.return_value = "Test output"
    mock_session_repository.return_value = "Test user"

    use_case = SendMarketOrderUseCase(
        mock_presenter,
        mock_config,
        mock_logger,
        mock_session_repository,
    )

    input_dto = SendMarketOrderInputDto(**fixture_send_market_order)
    input_dto.to_pfcf_dict = mocker.MagicMock()
    input_dto.to_pfcf_dict.return_value = fake_pfcf_dict
    with pytest.raises(ItemNotCreatedException) as exc:
        use_case.execute(input_dto)

    mock_validator.assert_called_once_with(input_dto.to_dict())
    mock_validator_instance.validate.assert_called_once_with()

    input_dto.to_pfcf_dict.assert_called_once_with(mock_config)

    mock_session_repository.get_current_user.assert_called_once()

    mock_config.EXCHANGE_TRADE.OrderObject.assert_called_once()
    mock_config.EXCHANGE_CLIENT.DTradeLib.Order.assert_called_once()

    mock_presenter.present.assert_not_called()
    mock_logger.log_info.assert_not_called()

    assert str(exc.value) == f"Order '{input_dto.order_account}' was not created correctly"


def test_send_market_order_if_order_result_has_error(mocker, fixture_send_market_order):
    fake_pfcf_dict = {
        "ACTNO": "12345678900",
        "PRODUCTID": "1234567890",
        "BS": "BUY",
        "ORDERTYPE": "MARKET",
        "PRICE": 100,
        "ORDERQTY": 10,
        "TIMEINFORCE": "IOC",
        "OPENCLOSE": "OPEN",
        "DTRADE": "NO",
        "NOTE": "Test note",
    }

    # mock all dependencies in the use case
    mock_presenter = mocker.patch.object(SendMarketOrderPresenterInterface, "present")
    mock_config = mocker.patch("src.app.cli_pfcf.config.Config")
    mock_config.EXCHANGE_CLIENT.DTradeLib.Order = mocker.MagicMock()

    mock_order_result = mocker.MagicMock()
    mock_order_result.SEQ = ""
    mock_order_result.ERRORCODE = "Test error code"
    mock_order_result.ERRORMSG = "Test error message"
    mock_order_result.ISSEND = True
    mock_order_result.NOTE = fixture_send_market_order["note"]

    mock_config.EXCHANGE_CLIENT.DTradeLib.Order.return_value = mock_order_result

    mock_order_obejct = mocker.MagicMock()
    mock_order_obejct.ACTNO = ""
    mock_order_obejct.PRODUCTID = ""
    mock_order_obejct.BS = ""
    mock_order_obejct.ORDERTYPE = ""
    mock_order_obejct.PRICE = 0
    mock_order_obejct.ORDERQTY = 0
    mock_order_obejct.TIMEINFORCE = ""
    mock_order_obejct.OPENCLOSE = ""
    mock_order_obejct.DTRADE = ""
    mock_order_obejct.NOTE = ""

    mock_config.EXCHANGE_TRADE.OrderObject = mocker.MagicMock()
    mock_config.EXCHANGE_TRADE.OrderObject.return_value = mock_order_obejct
    mock_logger = mocker.patch.object(LoggerInterface, "log_info")
    mock_session_repository = mocker.patch(
        "src.infrastructure.repositories.session_in_memory_repository.SessionInMemoryRepository"
    )
    mock_session_repository.get_current_user.return_value = "Test user"

    mock_validator = mocker.patch(
        "src.interactor.use_cases.send_market_order.SendMarketOrderInputDtoValidator"
    )
    mock_validator_instance = mock_validator.return_value
    mock_presenter.present.return_value = "Test output"
    mock_session_repository.return_value = "Test user"

    use_case = SendMarketOrderUseCase(
        mock_presenter,
        mock_config,
        mock_logger,
        mock_session_repository,
    )

    input_dto = SendMarketOrderInputDto(**fixture_send_market_order)
    input_dto.to_pfcf_dict = mocker.MagicMock()
    input_dto.to_pfcf_dict.return_value = fake_pfcf_dict

    with pytest.raises(SendMarketOrderFailedException) as exc:
        use_case.execute(input_dto)

    mock_validator.assert_called_once_with(input_dto.to_dict())
    mock_validator_instance.validate.assert_called_once_with()

    input_dto.to_pfcf_dict.assert_called_once_with(mock_config)

    mock_session_repository.get_current_user.assert_called_once()

    mock_config.EXCHANGE_TRADE.OrderObject.assert_called_once()
    mock_config.EXCHANGE_CLIENT.DTradeLib.Order.assert_called_once()

    mock_presenter.present.assert_not_called()
    mock_logger.log_info.assert_not_called()

    assert (
        str(exc.value)
        == "Send market order failed: Order not created: test error message with code test error code"
    )
