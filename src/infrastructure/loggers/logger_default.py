""" Module for LoggerDefault class."""

import logging
import os

from src.interactor.interfaces.logger.logger import LoggerInterface


class LoggerDefault(LoggerInterface):
    """LoggerDefault class."""

    def __init__(self):
        """Constructor."""

        # check if logs folder exists, if not, create it
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # configure logger
        logging.basicConfig(
            filename="logs/app.log",
            filemode="a",
            datefmt="%Y-%m-%d %H:%M:%S",
            format="%(asctime)-s - %(filename)s - %(lineno)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )

    def log_debug(self, message: str) -> None:
        """Log debug message.
        :param message: Message to log.
        """
        logging.debug(message)

    def log_info(self, message: str) -> None:
        """Log info message.
        :param message: Message to log.
        """
        logging.info(message)

    def log_warning(self, message: str) -> None:
        """Log warning message.
        :param message: Message to log.
        """
        logging.warning(message)

    def log_error(self, message: str) -> None:
        """Log error message.
        :param message: Message to log.
        """
        logging.error(message)

    def log_critical(self, message: str) -> None:
        """Log critical message.
        :param message: Message to log.
        """
        logging.critical(message)

    def log_exception(self, message: str) -> None:
        """Log exception message with exception info.
        :param message: Message to log.
        """
        logging.exception(message)
