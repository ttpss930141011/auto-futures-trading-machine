""" This module contains the ExitController class
"""

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.infrastructure.services.service_container import ServiceContainer


class MYTestController(CliMemoryControllerInterface):
    """ This class is a controller for testing purposes
    """

    def __init__(self, service_container: ServiceContainer):
        self.logger = service_container.logger
        self.config = service_container.config
        self.session_repository = service_container.session_repository

    def execute(self):
        """ This method executes the controller
        """
        print("Test controller")
        print(self.config.EXCHANGE_TRADE)
        print(self.config.EXCHANGE_TRADE.SideEnum)
        print(self.config.EXCHANGE_TRADE.SideEnum.Buy)
