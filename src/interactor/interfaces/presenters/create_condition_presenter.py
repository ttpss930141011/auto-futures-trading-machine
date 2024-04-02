""" Module for the UserLoginPresenterInterface
"""

from abc import ABC, abstractmethod
from typing import Dict

from src.interactor.dtos.create_condition_dtos import CreateConditionOutputDto


class CreateConditionPresenterInterface(ABC):
    """ Class for the Interface of the CreateConditionPresenter
    """

    @abstractmethod
    def present(self, output_dto: CreateConditionOutputDto) -> Dict:
        """ Present the output dto
        """
