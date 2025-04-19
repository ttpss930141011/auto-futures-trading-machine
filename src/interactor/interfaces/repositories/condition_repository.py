""" This module contains the interface for the ConditionRepository
"""
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict

from src.domain.entities.condition import Condition
from src.domain.value_objects import OrderOperation


class ConditionRepositoryInterface(ABC):
    """ This class is the interface for the ConditionRepository
    """

    @abstractmethod
    def get(self, condition_id: uuid.UUID) -> Optional[Condition]:
        """ Get a Condition by account

        :param condition_id: uuid.UUID
        :return: Condition
        """

    @abstractmethod
    def get_all(self) -> Dict[uuid.UUID, Condition]:
        """ Get all Conditions

        :return: Dict[ConditionId, Condition]
        """

    @abstractmethod
    def search_by_trigger_price(self, trigger_price: int) -> Optional[Condition]:
        """ Search Condition by trigger_price

        :param trigger_price: int
        :return: Dict[ConditionId, Condition]
        """

    @abstractmethod
    def create(self, action: OrderOperation, trigger_price: int, turning_point: int,
               quantity: int, take_profit_point: int, stop_loss_point: int,
               is_following: bool) -> Optional[Condition]:
        """ Create a new Condition"""

    @abstractmethod
    def delete(self, condition_id: uuid.UUID) -> bool:
        """ Delete a Condition by account

        :param condition_id: uuid.UUID
        :return: bool
        """

    @abstractmethod
    def delete_all(self) -> bool:
        """ Delete all users

        :return: bool
        """

    @abstractmethod
    def update(self, condition: Condition) -> Optional[Condition]:
        """ Update a Condition

        :param condition: Condition
        :return:
        """
