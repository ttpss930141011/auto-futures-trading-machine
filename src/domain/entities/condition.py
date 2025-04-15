""" This module has definition of the Condition entity
"""
from dataclasses import asdict, dataclass, field

from src.domain.value_objects import ConditionId, OrderOperation


@dataclass
class Condition:
    """Definition of the Condition entity
    :param condition_id: id
    :param action: the action to place the order, buy or sell
    :param trigger_price: the price to trigger the order
    :param order_price: the price to place the order, the price is depended on the action and the turning point
    :param quantity: the quantity of the order
    :param take_profit_price: the price to take profit
    :param stop_loss_price: the price to stop loss
    :param take_profit_point: the points to take profit
    :param stop_loss_point: the points to stop loss
    :param turning_point: the points to turn the order to place
    :param is_trigger: if the price is triggered, the order will be prepared to be placed
    :param is_following: if the order needs keep following the price
    :param is_ordered: if the order is placed
    :param is_exited: if the order is exited
    """

    condition_id: ConditionId
    action: OrderOperation
    trigger_price: int
    quantity: int
    turning_point: int = field(default=15)
    take_profit_point: int = field(default=90)
    stop_loss_point: int = field(default=30)
    take_profit_price: int = field(init=False)
    stop_loss_price: int = field(init=False)
    order_price: int = field(init=False)
    is_following: bool = field(default=False)
    is_trigger: bool = field(init=False, default=False)
    is_ordered: bool = field(init=False, default=False)
    is_exited: bool = field(init=False, default=False)

    def __post_init__(self):
        """Validate the entity"""
        if self.condition_id is None:
            raise ValueError("Condition ID is required")
        if self.action is None:
            raise ValueError("Action is required")
        if self.trigger_price is None:
            raise ValueError("Trigger price is required")
        if self.quantity is None:
            raise ValueError("Quantity is required")

        if self.action == OrderOperation.BUY:
            self.order_price = self.trigger_price + self.turning_point
            self.take_profit_price = self.order_price + self.take_profit_point
            self.stop_loss_price = self.order_price - self.stop_loss_point
        elif self.action == OrderOperation.SELL:
            self.order_price = self.trigger_price - self.turning_point
            self.take_profit_price = self.order_price - self.take_profit_point
            self.stop_loss_price = self.order_price + self.stop_loss_point
        else:
            raise ValueError("Action is not valid")

    @classmethod
    def from_dict(cls, data):
        """Convert data from a dictionary"""
        return cls(**data)

    def to_dict(self):
        """Convert data into dictionary"""
        return asdict(self)

    def __repr__(self):
        return f"<Condition {self.condition_id}>"

    def __str__(self):
        return f"<Condition {self.condition_id}>"
