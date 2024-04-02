""" Configuration file
"""

import os
import sys

from dotenv import load_dotenv

from src.interactor.interfaces.dealer_client.dealer_client import PFCFClientInterface

load_dotenv(encoding="utf8", dotenv_path=".env")


class Config(object):
    DEALER_CLIENT = None
    DEALER_TEST_URL = os.getenv("DEALER_TEST_URL", "")
    DEALER_PROD_URL = os.getenv("DEALER_PROD_URL", "")
    DEFAULT_SESSION_TIMEOUT = 43200
    DEFAULT_TAKE_PROFIT_POINT = 90
    DEFAULT_STOP_LOSS_POINT = 30

    def __init__(self, dealer_client: PFCFClientInterface | None = None):

        self.DEALER_CLIENT = dealer_client.get_client() if dealer_client is not None else None

        if self.DEALER_CLIENT is None:
            print("FAIL TO LOAD DEALER_CLIENT.")
            sys.exit(1)
        if self.DEALER_TEST_URL is None:
            print("Specify DEALER_TEST_URL as environment variable.")
            sys.exit(1)
        if self.DEALER_PROD_URL is None:
            print("Specify DEALER_PROD_URL as environment variable.")
            sys.exit(1)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]
