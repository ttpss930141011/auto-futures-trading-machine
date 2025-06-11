import pytest
from unittest.mock import MagicMock

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


def test_send_market_order(fixture_send_market_order):
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
    mock_presenter = MagicMock(spec=SendMarketOrderPresenterInterface)
    mock_service_container = MagicMock()
    mock_service_container.exchange_client.DTradeLib.Order = MagicMock()

    mock_order_result = MagicMock()
    mock_order_result.SEQ = "Test order serial"
    mock_order_result.ERRORCODE = ""
    mock_order_result.ERRORMSG = ""
    mock_order_result.ISSEND = True
    mock_order_result.NOTE = fixture_send_market_order["note"]

    mock_service_container.exchange_client.DTradeLib.Order.return_value = mock_order_result

    mock_order_obejct = MagicMock()
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

    mock_service_container.exchange_trade.OrderObject = MagicMock()
    mock_service_container.exchange_trade.OrderObject.return_value = mock_order_obejct
    mock_logger = MagicMock(spec=LoggerInterface)
    mock_session_repository = MagicMock()
    mock_session_repository.get_current_user.return_value = "Test user"

    from src.interactor.validations.send_market_order_validator import SendMarketOrderInputDtoValidator
    mock_validator = MagicMock(spec=SendMarketOrderInputDtoValidator)
    mock_presenter.present.return_value = "Test output"

    use_case = SendMarketOrderUseCase(
        mock_presenter,
        mock_service_container,
        mock_logger,
        mock_session_repository,
    )

    input_dto = SendMarketOrderInputDto(**fixture_send_market_order)
    input_dto.to_pfcf_dict = MagicMock()
    input_dto.to_pfcf_dict.return_value = fake_pfcf_dict
    
    # Mock the validator creation
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.interactor.use_cases.send_market_order.SendMarketOrderInputDtoValidator", lambda x: mock_validator)
        result = use_case.execute(input_dto)

    mock_validator.validate.assert_called_once_with()
    input_dto.to_pfcf_dict.assert_called_once_with(mock_service_container)

    mock_session_repository.get_current_user.assert_called_once()

    mock_service_container.exchange_trade.OrderObject.assert_called_once()
    mock_service_container.exchange_client.DTradeLib.Order.assert_called_once()

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


def test_send_market_order_if_user_is_none(fixture_send_market_order):
    # mock all dependencies in the use case
    mock_presenter = MagicMock(spec=SendMarketOrderPresenterInterface)
    mock_service_container = MagicMock()
    mock_logger = MagicMock(spec=LoggerInterface)
    mock_session_repository = MagicMock()
    mock_session_repository.get_current_user.return_value = None

    from src.interactor.validations.send_market_order_validator import SendMarketOrderInputDtoValidator
    mock_validator = MagicMock(spec=SendMarketOrderInputDtoValidator)

    use_case = SendMarketOrderUseCase(
        mock_presenter,
        mock_service_container,
        mock_logger,
        mock_session_repository,
    )

    input_dto = SendMarketOrderInputDto(**fixture_send_market_order)
    input_dto.to_pfcf_dict = MagicMock()

    # Mock the validator creation
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.interactor.use_cases.send_market_order.SendMarketOrderInputDtoValidator", lambda x: mock_validator)
        with pytest.raises(LoginFailedException) as exc:
            use_case.execute(input_dto)

    mock_validator.validate.assert_called_once_with()
    mock_session_repository.get_current_user.assert_called_once()

    mock_presenter.present.assert_not_called()
    mock_logger.log_info.assert_not_called()
    input_dto.to_pfcf_dict.assert_not_called()

    assert str(exc.value) == "Login failed: User not logged in"


def test_send_market_order_if_order_result_is_none(fixture_send_market_order):
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
    mock_presenter = MagicMock(spec=SendMarketOrderPresenterInterface)
    mock_service_container = MagicMock()
    mock_service_container.exchange_client.DTradeLib.Order = MagicMock()

    mock_order_result = None

    mock_service_container.exchange_client.DTradeLib.Order.return_value = mock_order_result

    mock_order_obejct = MagicMock()
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

    mock_service_container.exchange_trade.OrderObject = MagicMock()
    mock_service_container.exchange_trade.OrderObject.return_value = mock_order_obejct
    mock_logger = MagicMock(spec=LoggerInterface)
    mock_session_repository = MagicMock()
    mock_session_repository.get_current_user.return_value = "Test user"

    from src.interactor.validations.send_market_order_validator import SendMarketOrderInputDtoValidator
    mock_validator = MagicMock(spec=SendMarketOrderInputDtoValidator)
    mock_presenter.present.return_value = "Test output"

    use_case = SendMarketOrderUseCase(
        mock_presenter,
        mock_service_container,
        mock_logger,
        mock_session_repository,
    )

    input_dto = SendMarketOrderInputDto(**fixture_send_market_order)
    input_dto.to_pfcf_dict = MagicMock()
    input_dto.to_pfcf_dict.return_value = fake_pfcf_dict
    
    # Mock the validator creation
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.interactor.use_cases.send_market_order.SendMarketOrderInputDtoValidator", lambda x: mock_validator)
        with pytest.raises(ItemNotCreatedException) as exc:
            use_case.execute(input_dto)

    mock_validator.validate.assert_called_once_with()
    input_dto.to_pfcf_dict.assert_called_once_with(mock_service_container)

    mock_session_repository.get_current_user.assert_called_once()

    mock_service_container.exchange_trade.OrderObject.assert_called_once()
    mock_service_container.exchange_client.DTradeLib.Order.assert_called_once()

    mock_presenter.present.assert_not_called()
    mock_logger.log_info.assert_not_called()

    assert str(exc.value) == f"Order '{input_dto.order_account}' was not created correctly"


def test_send_market_order_if_order_result_has_error(fixture_send_market_order):
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
    mock_presenter = MagicMock(spec=SendMarketOrderPresenterInterface)
    mock_service_container = MagicMock()
    mock_service_container.exchange_client.DTradeLib.Order = MagicMock()

    mock_order_result = MagicMock()
    mock_order_result.SEQ = ""
    mock_order_result.ERRORCODE = "Test error code"
    mock_order_result.ERRORMSG = "Test error message"
    mock_order_result.ISSEND = True
    mock_order_result.NOTE = fixture_send_market_order["note"]

    mock_service_container.exchange_client.DTradeLib.Order.return_value = mock_order_result

    mock_order_obejct = MagicMock()
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

    mock_service_container.exchange_trade.OrderObject = MagicMock()
    mock_service_container.exchange_trade.OrderObject.return_value = mock_order_obejct
    mock_logger = MagicMock(spec=LoggerInterface)
    mock_session_repository = MagicMock()
    mock_session_repository.get_current_user.return_value = "Test user"

    from src.interactor.validations.send_market_order_validator import SendMarketOrderInputDtoValidator
    mock_validator = MagicMock(spec=SendMarketOrderInputDtoValidator)
    mock_presenter.present.return_value = "Test output"

    use_case = SendMarketOrderUseCase(
        mock_presenter,
        mock_service_container,
        mock_logger,
        mock_session_repository,
    )

    input_dto = SendMarketOrderInputDto(**fixture_send_market_order)
    input_dto.to_pfcf_dict = MagicMock()
    input_dto.to_pfcf_dict.return_value = fake_pfcf_dict

    # Mock the validator creation
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.interactor.use_cases.send_market_order.SendMarketOrderInputDtoValidator", lambda x: mock_validator)
        with pytest.raises(SendMarketOrderFailedException) as exc:
            use_case.execute(input_dto)

    mock_validator.validate.assert_called_once_with()
    input_dto.to_pfcf_dict.assert_called_once_with(mock_service_container)

    mock_session_repository.get_current_user.assert_called_once()

    mock_service_container.exchange_trade.OrderObject.assert_called_once()
    mock_service_container.exchange_client.DTradeLib.Order.assert_called_once()

    mock_presenter.present.assert_not_called()
    mock_logger.log_info.assert_not_called()

    assert (
        str(exc.value)
        == "Send market order failed: Order not created: test error message with code test error code"
    )