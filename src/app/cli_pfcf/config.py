""" Configuration file
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv(encoding="utf8", dotenv_path=".env")


class Config(object):
    EXCHANGE_CLIENT = None
    EXCHANGE_TRADE = None
    EXCHANGE_DECIMAL = None
    EXCHANGE_TEST_URL = os.getenv("DEALER_TEST_URL", "")
    EXCHANGE_PROD_URL = os.getenv("DEALER_PROD_URL", "")
    DEFAULT_SESSION_TIMEOUT = 43200
    DEFAULT_TAKE_PROFIT_POINT = 90
    DEFAULT_STOP_LOSS_POINT = 30

    def __init__(self, exchange_api=None):

        self.EXCHANGE_CLIENT = exchange_api.client if exchange_api is not None else None
        self.EXCHANGE_TRADE = exchange_api.trade if exchange_api is not None else None
        self.EXCHANGE_DECIMAL = exchange_api.decimal if exchange_api is not None else None

        if self.EXCHANGE_CLIENT is None:
            print("FAIL TO LOAD DEALER_CLIENT.")
            sys.exit(1)
        if self.EXCHANGE_TRADE is None:
            print("FAIL TO LOAD DEALER_TRADE.")
            sys.exit(1)
        if self.EXCHANGE_TEST_URL is None:
            print("Specify DEALER_TEST_URL as environment variable.")
            sys.exit(1)
        if self.EXCHANGE_PROD_URL is None:
            print("Specify DEALER_PROD_URL as environment variable.")
            sys.exit(1)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]
