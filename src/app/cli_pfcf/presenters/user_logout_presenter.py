""" Module for the UserLogoutPresenter
"""

from typing import Dict

from src.interactor.dtos.user_logout_dtos import UserLogoutOutputDto
from src.interactor.interfaces.presenters.user_logout_presenter import UserLogoutPresenterInterface


class UserLogoutPresenter(UserLogoutPresenterInterface):
    """ Class for the
    """

    def present(self, output_dto: UserLogoutOutputDto) -> Dict:
        """ Present the UserLogout
        :param output_dto: UserLogoutOutputDto
        :return: Dict
        """
        return {
            "action": "logout",
            "message": f"User logout {'successfully' if output_dto.is_success else 'failed'}",
            "account": output_dto.account,
            "is_success": output_dto.is_success
        }
