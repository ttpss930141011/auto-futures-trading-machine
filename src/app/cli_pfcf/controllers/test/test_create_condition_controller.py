# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from src.app.cli_pfcf.controllers.create_condition_controller import CreateConditionController
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


def test_get_user_input(monkeypatch, mocker, fixture_create_condition):
    action_input = "b"
    target_price_input = fixture_create_condition["trigger_price"]
    turning_point_input = fixture_create_condition["turning_point"]
    quantity_input = fixture_create_condition["quantity"]
    take_profit_point_input = fixture_create_condition["take_profit_point"]
    stop_loss_point_input = fixture_create_condition["stop_loss_point"]
    following_input = "y"

    # manually set the user inputs
    fake_user_inputs = iter(
        [action_input, target_price_input, turning_point_input, quantity_input, take_profit_point_input,
         stop_loss_point_input, following_input])
    monkeypatch.setattr('builtins.input', lambda _: next(fake_user_inputs))

    # initialize the CreateConditionController
    service_container_mock = mocker.patch('src.app.cli_pfcf.controllers.user_login_controller.ServiceContainer')
    service_container_mock.logger = mocker.patch.object(LoggerInterface, "log_info")
    service_container_mock.config = mocker.patch('src.app.cli_pfcf.config.Config')
    service_container_mock.condition_repository = mocker.patch.object(ConditionRepositoryInterface, "create")
    service_container_mock.session_repository = mocker.patch.object(SessionRepositoryInterface, "is_user_logged_in")

    input_dto = CreateConditionController(service_container_mock)._get_user_input()

    assert input_dto.action == fixture_create_condition["action"]
    assert input_dto.trigger_price == fixture_create_condition["trigger_price"]
    assert input_dto.turning_point == fixture_create_condition["turning_point"]
    assert input_dto.quantity == fixture_create_condition["quantity"]
    assert input_dto.take_profit_point == fixture_create_condition["take_profit_point"]
    assert input_dto.stop_loss_point == fixture_create_condition["stop_loss_point"]
    assert input_dto.is_following == fixture_create_condition["is_following"]
