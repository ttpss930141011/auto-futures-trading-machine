""" Module for CreateCondition Dtos
"""

from dataclasses import dataclass, asdict

from src.domain.entities.condition import Condition
from src.domain.value_objects import OrderOperation


@dataclass
class CreateConditionInputDto:
    """ Data Transfer Object for creating condition"""
    action: OrderOperation
    trigger_price: int
    turning_point: int
    quantity: int
    take_profit_point: int
    stop_loss_point: int
    is_following: bool = True

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)


@dataclass
class CreateConditionOutputDto:
    """ Data Transfer Object for creating condition"""
    condition: Condition
