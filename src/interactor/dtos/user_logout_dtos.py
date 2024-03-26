""" Module for CreateUser Dtos
"""

from dataclasses import dataclass, asdict


@dataclass
class UserLogoutInputDto:
    """ Input Dto for create profession """
    account: str

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)


@dataclass
class UserLogoutOutputDto:
    """ Output Dto for create profession """
    account: str
    is_success: bool
