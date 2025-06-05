""" This module provides the base class BaseInputValidator for input validation
"""

from typing import Dict

"""This module provides the base class for input validation without external dependencies."""


class BaseInputValidator:
    """ This class provides the base class for input validation
    """

    def __init__(self, data: Dict[str, str]):
        self.data = data
        self.errors: Dict = {}

    def verify(self, schema: Dict) -> None:
        """ Validates the input data against the provided schema
        :param schema: The schema to validate against
        :return: None
        :raises ValueError: If the input data is invalid.
        """
        self.errors = {}
        for field, rules in schema.items():
            data_present = field in self.data
            if rules.get('required', False) and not data_present:
                self.errors.setdefault(field, []).append('required field')
                continue
            if not data_present:
                continue
            value = self.data[field]
            if value is None:
                self.errors.setdefault(field, []).append('null value not allowed')
                continue
            expected_type = rules.get('type')
            if expected_type == 'string':
                if not isinstance(value, str):
                    self.errors.setdefault(field, []).append('must be a string')
                    continue
                if not rules.get('empty', True) and value == '':
                    self.errors.setdefault(field, []).append('empty values not allowed')
                    continue
                length = len(value)
                if 'minlength' in rules and length < rules['minlength']:
                    self.errors.setdefault(field, []).append(f"min length is {rules['minlength']}")
                if 'maxlength' in rules and length > rules['maxlength']:
                    self.errors.setdefault(field, []).append(f"max length is {rules['maxlength']}")
            elif expected_type == 'integer':
                if not isinstance(value, int):
                    self.errors.setdefault(field, []).append('must be an integer')
            elif expected_type == 'boolean':
                if not isinstance(value, bool):
                    self.errors.setdefault(field, []).append('must be a boolean')
            if 'allowed' in rules and value not in rules['allowed']:
                self.errors.setdefault(field, []).append(f"unallowed value {value}")
        if self.errors:
            self._raise_validation_error()

    def _raise_validation_error(self):
        messages = []
        for field in sorted(self.errors):
            for msg in self.errors[field]:
                messages.append(f"{field.capitalize()}: {msg}")
        raise ValueError("\n".join(messages))
