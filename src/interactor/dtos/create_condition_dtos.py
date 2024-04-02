""" Module for CreateCondition Dtos
"""

from dataclasses import dataclass, asdict
from typing import Literal

from src.domain.entities.condition import Condition


@dataclass
class CreateConditionInputDto:
    """ Data Transfer Object for creating condition"""
    action: Literal["buy", "sell"]
    trigger_price: int
    turning_point: int
    quantity: int
    take_profit_point: int
    stop_loss_point: int

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)


@dataclass
class CreateConditionOutputDto:
    """ Data Transfer Object for creating condition"""
    condition: Condition
