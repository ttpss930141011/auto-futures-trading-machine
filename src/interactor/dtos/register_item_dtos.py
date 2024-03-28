""" Module for CreateUser Dtos
"""

from dataclasses import dataclass, asdict


@dataclass
class RegisterItemInputDto:
    """ Data Transfer Object for register item"""
    account: str
    item_code: str

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)


@dataclass
class RegisterItemOutputDto:
    """ Data Transfer Object for register item"""
    account: str
    item_code: str
    is_registered: bool
