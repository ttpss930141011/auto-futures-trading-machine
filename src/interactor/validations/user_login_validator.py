from typing import Dict

from src.interactor.validations.base_input_validator import BaseInputValidator


class UserLoginInputDtoValidator(BaseInputValidator):
    """ Validates the input data for UserLoginUseCase.
    :param input_data: The input data to be validated.
    """

    def __init__(self, input_data: Dict) -> None:
        super().__init__(input_data)
        self.input_data = input_data
        self.__schema = {
            "account": {
                "type": "string",
                "minlength": 11,
                "maxlength": 80,
                "required": True,
                "empty": False
            },
            "password": {
                "type": "string",
                "minlength": 5,
                "maxlength": 200,
                "required": True,
                "empty": False
            },
            "ip_address": {
                "type": "string",
                "minlength": 5,
                "maxlength": 200,
                "required": True,
                "empty": False
            }
        }

    def validate(self) -> None:
        """ Validates the input data
        """
        # Verify the input data using BaseInputValidator method
        super().verify(self.__schema)
