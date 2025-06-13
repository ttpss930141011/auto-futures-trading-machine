""" This module contains the ProcessHandler for Cli that uses Memory repository
"""

from typing import Dict, Literal

from src.app.cli_pfcf.interfaces.cli_memory_controller_interface import CliMemoryControllerInterface
from src.infrastructure.services.service_container import ServiceContainer


class CliMemoryProcessHandler:
    """The ProcessHandler for Cli that uses Memory repository"""

    def __init__(self, service_container: ServiceContainer) -> None:
        self.logger = service_container.logger
        self.session_repository = service_container.session_repository
        self.options: Dict = {}
        self.public_options = []
        self.protected_options = []

    def add_option(
        self,
        option: str,
        controller: CliMemoryControllerInterface,
        controller_type: Literal["public", "protected"] = "public",
    ) -> None:
        """Add an option to the ProcessHandler
        @param option:
        @param controller:
        @param controller_type:
        """

        self.options[option] = controller
        if controller_type == "public":
            self.public_options.append(option)
        elif controller_type == "protected":
            self.protected_options.append(option)
        else:
            raise ValueError("Invalid controller type")

    def show_options(self):
        """Print  the options to the ProcessHandler
        :return: None
        """
        for option, controller in self.options.items():
            if option in self.public_options:
                print(f"{option}: {controller.__class__.__name__}")
            if self.session_repository.is_user_logged_in() and option in self.protected_options:
                print(f"{option}: {controller.__class__.__name__}")

    def execute(self) -> None:
        """Execute the ProcessHandler
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
                except (RuntimeError, ValueError, OSError) as exception:
                    print(f"\nERROR: {str(exception)}\n")
                    self.logger.log_exception(str(exception))
            else:
                print("Invalid choice.")
                self.logger.log_info(f"Invalid user choice: {option}")
