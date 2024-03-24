""" This module contains the ProcessHandler for Cli that uses Memory repository
"""

from typing import Dict

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.interactor.errors.error_classes import FieldValueNotPermittedException
from src.interactor.interfaces.logger.logger import LoggerInterface


class CliMemoryProcessHandler:
    """ The ProcessHandler for Cli that uses Memory repository
    """

    def __init__(self, logger: LoggerInterface) -> None:
        self.logger = logger
        self.options: Dict = {}

    def add_option(
            self,
            option: str,
            controller: CliMemoryControllerInterface
    ) -> None:
        """ Add an option to the ProcessHandler
        :param option: The option
        :param controller: The controller for the option
        :return: None
        """
        self.options[option] = controller

    def show_options(self):
        """ Print  the options to the ProcessHandler
        :return: None
        """
        for option, controller in self.options.items():
            print(f"{option}: {controller.__class__.__name__}")

    def execute(self) -> None:
        """ Execute the ProcessHandler
        :return: None
        """
        while True:
            print("Please choose an option:")
            self.show_options()
            choice = input("> ")
            option = self.options.get(choice)
            if option:
                try:
                    option.execute()
                except (
                        ValueError,
                        FieldValueNotPermittedException
                ) as exception:
                    print(f'\nERROR: {str(exception)}\n')
                    self.logger.log_exception(str(exception))
            else:
                print("Invalid choice.")
                self.logger.log_info(f"Invalid user choice: {option}")
