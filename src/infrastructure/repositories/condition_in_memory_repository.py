""" Module for ConditionInMemoryRepository
"""
import uuid
from typing import Dict

from src.domain.entities.condition import Condition
from src.domain.value_objects import ConditionId, OrderOperation
from src.interactor.interfaces.repositories.condition_repository import ConditionRepositoryInterface


class ConditionInMemoryRepository(ConditionRepositoryInterface):
    """ InMemory Repository for Condition
    """

    def __init__(self) -> None:
        self._data: Dict[ConditionId, Condition] = {}

    def get(self, condition_id: ConditionId) -> Condition:
        """ Get Condition by condition_id

        :param condition_id: ConditionId
        :return: Condition
        """
        return self._data.get(condition_id)

    def get_all(self) -> Dict[ConditionId, Condition]:
        """ Get all Conditions

        :return: Dict[ConditionId, Condition]
        """
        return self._data

    # search by target price
    def search_by_trigger_price(self, trigger_price: int) -> Dict[ConditionId, Condition]:
        """ Search Condition by trigger_price

        :param trigger_price: int
        :return: Dict[ConditionId, Condition]
        """

        return {condition_id: condition for condition_id, condition in self._data.items() if
                condition.trigger_price == trigger_price}

    def create(self, action: OrderOperation, trigger_price: int, turning_point: int,
               quantity: int, take_profit_point: int, stop_loss_point: int,
               is_following: bool) -> Condition:
        """ Create a new Condition"""
        condition_id = uuid.uuid4()
        condition = Condition(
            condition_id=condition_id,
            action=action,
            trigger_price=trigger_price,
            quantity=quantity,
            turning_point=turning_point,
            take_profit_point=take_profit_point,
            stop_loss_point=stop_loss_point,
            is_following=is_following
        )
        self._data[condition.condition_id] = condition
        return condition

    def delete(self, condition_id: ConditionId) -> bool:
        """
        Delete Condition by condition_id
        :param condition_id: str
        :return: bool
        """
        if condition_id in self._data:
            del self._data[condition_id]
            return True
        return False

    def delete_all(self) -> bool:
        """
        Delete
        all
        conditions

        :return: bool
        """
        self._data = {}
        return True

    def update(self, condition: Condition) -> Condition:
        """
        Update Condition
        :param condition: Condition
        :return: Condition
        """
        self._data[condition.condition_id] = condition
        return condition
