""" Configuration file
"""

import os
import sys
from src.infrastructure.pfcf_client.api import PFCFApi

try:
    from dotenv import load_dotenv

    load_dotenv(encoding="utf8", dotenv_path=".env")
except ImportError:
    pass


class Config(object):
    """Configuration for the application"""

    EXCHANGE_CLIENT = None
    EXCHANGE_TRADE = None
    EXCHANGE_DECIMAL = None
    EXCHANGE_TEST_URL = os.getenv("DEALER_TEST_URL", "")
    EXCHANGE_PROD_URL = os.getenv("DEALER_PROD_URL", "")
    DEFAULT_SESSION_TIMEOUT = 43200
    DEFAULT_TAKE_PROFIT_POINT = 90
    DEFAULT_STOP_LOSS_POINT = 30

    # ZMQ configuration
    ZMQ_HOST = os.getenv("ZMQ_HOST", "127.0.0.1")
    ZMQ_TICK_PORT = int(os.getenv("ZMQ_TICK_PORT", "5555"))
    ZMQ_SIGNAL_PORT = int(os.getenv("ZMQ_SIGNAL_PORT", "5556"))

    @property
    def ZMQ_TICK_PUB_ADDRESS(self) -> str:
        """Get the ZMQ tick publisher address."""
        return f"tcp://{self.ZMQ_HOST}:{self.ZMQ_TICK_PORT}"

    @property
    def ZMQ_SIGNAL_PULL_ADDRESS(self) -> str:
        """Get the ZMQ signal puller address."""
        return f"tcp://{self.ZMQ_HOST}:{self.ZMQ_SIGNAL_PORT}"

    @property
    def ZMQ_TICK_SUB_CONNECT_ADDRESS(self) -> str:
        """Get the ZMQ tick subscriber connect address."""
        return f"tcp://localhost:{self.ZMQ_TICK_PORT}"

    @property
    def ZMQ_SIGNAL_PUSH_CONNECT_ADDRESS(self) -> str:
        """Get the ZMQ signal pusher connect address."""
        return f"tcp://localhost:{self.ZMQ_SIGNAL_PORT}"

    def __init__(self, exchange_api=PFCFApi):

        self.EXCHANGE_CLIENT = (
            getattr(exchange_api, "client", None) if exchange_api is not None else None
        )
        self.EXCHANGE_TRADE = (
            getattr(exchange_api, "trade", None) if exchange_api is not None else None
        )
        self.EXCHANGE_DECIMAL = (
            getattr(exchange_api, "decimal", None) if exchange_api is not None else None
        )
        self.EXCHANGE_TEST_URL = os.getenv("DEALER_TEST_URL", "")
        self.EXCHANGE_PROD_URL = os.getenv("DEALER_PROD_URL", "")

        if self.EXCHANGE_CLIENT is None:
            print("FAIL TO LOAD DEALER_CLIENT.")
            sys.exit(1)
        if self.EXCHANGE_TRADE is None:
            print("FAIL TO LOAD DEALER_TRADE.")
            sys.exit(1)
        if not self.EXCHANGE_TEST_URL:
            print("Specify DEALER_TEST_URL as environment variable.")
            sys.exit(1)
        if not self.EXCHANGE_PROD_URL:
            print("Specify DEALER_PROD_URL as environment variable.")
            sys.exit(1)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]
