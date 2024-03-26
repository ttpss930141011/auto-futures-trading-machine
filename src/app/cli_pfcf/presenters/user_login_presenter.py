""" Module for the UserLoginPresenter
"""

from typing import Dict

from src.interactor.dtos.user_login_dtos \
    import UserLoginOutputDto
from src.interactor.interfaces.presenters.user_login_presenter \
    import UserLoginPresenterInterface


class UserLoginPresenter(UserLoginPresenterInterface):
    """ Class for the UserLoginPresenter
    """

    def present(self, output_dto: UserLoginOutputDto) -> Dict:
        """ Present the UserLogin
        :param output_dto: UserLoginOutputDto
        :return: Dict
        """
        return {
            "action": "user_login",
            "message": "User logged in successfully",
            "account": output_dto.user.account,
            "ip_address": output_dto.user.ip_address,
        }
