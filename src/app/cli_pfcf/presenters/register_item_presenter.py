""" Module for the RegisterItemPresenter
"""

from typing import Dict

from src.interactor.dtos.register_item_dtos import RegisterItemOutputDto
from src.interactor.interfaces.presenters.register_item_presenter import RegisterItemPresenterInterface


class RegisterItemPresenter(RegisterItemPresenterInterface):
    """ Class for the RegisterItemPresenter
    """

    def present(self, output_dto: RegisterItemOutputDto) -> Dict:
        """ Present the RegisterItem
        :param output_dto: RegisterItemOutputDto
        :return: Dict
        """
        return {
            "action": "register_item",
            "message": "User registered successfully",
        }
