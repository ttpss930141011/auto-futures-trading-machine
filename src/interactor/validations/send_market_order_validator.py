from typing import Dict

from src.interactor.validations.base_input_validator import BaseInputValidator


class SendMarketOrderInputDtoValidator(BaseInputValidator):
    """ Validates the input data for RegisterItemUseCase.
    :param input_data: The input data to be validated.
    """

    def __init__(self, input_data: Dict) -> None:
        super().__init__(input_data)
        self.input_data = input_data
        self.__schema = {
            "order_account": {
                "type": "string",
                "required": True,
                "empty": False
            },
            "item_code": {
                "type": "string",
                "required": True,
                "empty": False
            },
            "side": {
                "type": "string",
                "allowed": ["buy", "sell"],
                "required": True,
                "empty": False
            },
            "order_type": {
                "type": "string",
                "allowed": ["Limit", "Market", "MarketPrice"],
                "required": True,
                "empty": False
            },
            "price": {
                "type": "float",
                "required": True,
                "empty": False
            },
            "quantity": {
                "type": "integer",
                "required": True,
                "empty": False
            },
            "time_in_force": {
                "type": "string",
                "allowed": ["ROD", "IOC", "FOK"],
                "required": True,
                "empty": False
            },
            "open_close": {
                "type": "string",
                "allowed": ["Y", "N", "AUTO"],
                "required": True,
                "empty": False
            },
            "day_trade": {
                "type": "string",
                "allowed": ["Y", "N"],
                "required": True,
                "empty": False
            },
            "note": {
                "type": "string",
                "minlength": 0,
                "maxlength": 10,
                "required": False,
                "empty": True
            }

        }

    def validate(self) -> None:
        """ Validates the input data
        """
        # Verify the input data using BaseInputValidator method
        super().verify(self.__schema)
