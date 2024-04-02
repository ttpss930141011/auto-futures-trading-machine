from typing import Dict

from src.interactor.validations.base_input_validator import BaseInputValidator


class CreateConditionInputDtoValidator(BaseInputValidator):
    """ Validates the input data for RegisterItemUseCase.
    :param input_data: The input data to be validated.
    """

    def __init__(self, input_data: Dict) -> None:
        super().__init__(input_data)
        self.input_data = input_data
        self.__schema = {
            "action": {
                "type": "string",
                "allowed": ["buy", "sell"],
                "required": True,
                "empty": False
            },
            "trigger_price": {
                "type": "integer",
                "required": True,
                "empty": False
            },
            "turning_point": {
                "type": "integer",
                "required": True,
                "empty": False
            },
            "quantity": {
                "type": "integer",
                "required": True,
                "empty": False
            },
            "take_profit_point": {
                "type": "integer",
                "required": True,
                "empty": False
            },
            "stop_loss_point": {
                "type": "integer",
                "required": True,
                "empty": False
            },

        }

    def validate(self) -> None:
        """ Validates the input data
        """
        # Verify the input data using BaseInputValidator method
        super().verify(self.__schema)
