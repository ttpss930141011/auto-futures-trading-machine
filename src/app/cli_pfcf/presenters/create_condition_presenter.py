""" Module for the CreateConditionPresenter
"""

from typing import Dict

from src.interactor.dtos.create_condition_dtos import CreateConditionOutputDto
from src.interactor.interfaces.presenters.create_condition_presenter import CreateConditionPresenterInterface


class CreateConditionPresenter(CreateConditionPresenterInterface):
    """ Class for the CreateConditionPresenter
    """

    def present(self, output_dto: CreateConditionOutputDto) -> Dict:
        """ Present the output dto
        """
        return {
            "action": "create_condition",
            "message": f"Condition {output_dto.condition.condition_id} is created successfully",
            "condition": output_dto.condition.to_dict()
        }
