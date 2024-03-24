""" Configuration file
"""

import os
import sys

from dotenv import load_dotenv

from src.infrastructure.pfcf_client import client

load_dotenv(encoding="utf8", dotenv_path=".env")


class Config(object):
    DEALER_CLIENT = client
    DEALER_TEST_URL = os.getenv("DEALER_TEST_URL", "")
    DEALER_PROD_URL = os.getenv("DEALER_PROD_URL", "")

    def __init__(self):
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
