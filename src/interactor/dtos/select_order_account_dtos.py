""" Module for SelectOrderAccount Dtos
"""

from dataclasses import dataclass, asdict


@dataclass
class SelectOrderAccountInputDto:
    """ Data Transfer Object for selecting order account"""
    index: int
    order_account: str

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)


@dataclass
class SelectOrderAccountOutputDto:
    """ Data Transfer Object for selecting order account"""
    is_select_order_account: bool
    order_account: str
