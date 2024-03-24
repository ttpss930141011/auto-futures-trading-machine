""" This module contains the ExitController class
"""

import sys

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface


class ExitController(CliMemoryControllerInterface):
    """ This class is a controller for exiting the program
    """

    def execute(self):
        """ This method executes the controller, exiting the program
        """
        print("Exiting the program")
        sys.exit()
