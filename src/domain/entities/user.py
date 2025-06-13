""" This module has definition of the Window entity
"""
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class User:
    """Definition of the User entity"""

    account: str
    password: str
    ip_address: str
    client: Any

    def __post_init__(self):
        if self.account is None:
            raise TypeError("account should be setup")
        if self.password is None:
            raise TypeError("password should be setup")
        if self.ip_address is None:
            raise TypeError("ip_address should be setup")
        if self.client is None:
            raise TypeError("client should be setup")

    @classmethod
    def from_dict(cls, data):
        """Convert data from a dictionary"""
        return cls(**data)

    def to_dict(self):
        """Convert data into dictionary"""
        return asdict(self)

    def __repr__(self):
        return f"<User {self.account}>"

    def __str__(self):
        return f"<User {self.account}>"
