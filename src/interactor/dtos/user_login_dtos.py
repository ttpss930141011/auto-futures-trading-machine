""" Module for CreateUser Dtos
"""

from dataclasses import dataclass, asdict

from src.domain.entities.user import User


@dataclass
class UserLoginInputDto:
    """ Input Dto for create profession """
    account: str
    password: str
    ip_address: str

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)


@dataclass
class UserLoginOutputDto:
    """ Output Dto for create profession """
    user: User
