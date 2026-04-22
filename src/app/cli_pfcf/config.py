""" Configuration file
"""

import os

try:
    from dotenv import load_dotenv

    load_dotenv(encoding="utf8", dotenv_path=".env")
except ImportError:
    pass


class Config(object):
    """Configuration for the application.

    This class follows the Single Responsibility Principle by only handling
    configuration values and not managing API instances or business logic.
    """

    # Exchange URLs - will be loaded in __init__
    EXCHANGE_TEST_URL = ""
    EXCHANGE_PROD_URL = ""

    # Application defaults
    DEFAULT_SESSION_TIMEOUT = 43200
    DEFAULT_TAKE_PROFIT_POINT = 90
    DEFAULT_STOP_LOSS_POINT = 30

    # ZMQ configuration
    ZMQ_HOST = os.getenv("ZMQ_HOST", "127.0.0.1")
    ZMQ_TICK_PORT = int(os.getenv("ZMQ_TICK_PORT", "5555"))
    ZMQ_SIGNAL_PORT = int(os.getenv("ZMQ_SIGNAL_PORT", "5556"))

    # DLL Gateway configuration
    DLL_GATEWAY_HOST = os.getenv("DLL_GATEWAY_HOST", "127.0.0.1")
    DLL_GATEWAY_PORT = int(os.getenv("DLL_GATEWAY_PORT", "5557"))
    DLL_GATEWAY_REQUEST_TIMEOUT_MS = int(os.getenv("DLL_GATEWAY_REQUEST_TIMEOUT_MS", "5000"))
    DLL_GATEWAY_RETRY_COUNT = int(os.getenv("DLL_GATEWAY_RETRY_COUNT", "3"))

    # Exchange adapter selection: "pfcf" (real PFCF DLL) or "simulator" (in-memory)
    EXCHANGE_MODE = os.getenv("EXCHANGE_MODE", "pfcf").lower()

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

    @property
    def DLL_GATEWAY_BIND_ADDRESS(self) -> str:
        """Get the DLL Gateway server bind address."""
        return f"tcp://*:{self.DLL_GATEWAY_PORT}"

    @property
    def DLL_GATEWAY_CONNECT_ADDRESS(self) -> str:
        """Get the DLL Gateway client connect address."""
        return f"tcp://{self.DLL_GATEWAY_HOST}:{self.DLL_GATEWAY_PORT}"

    def __init__(self) -> None:
        """Initialize the configuration.

        Raises:
            ValueError: If required environment variables are missing or invalid.
        """
        self.EXCHANGE_TEST_URL = os.getenv("DEALER_TEST_URL", "")
        self.EXCHANGE_PROD_URL = os.getenv("DEALER_PROD_URL", "")

        if not self.EXCHANGE_TEST_URL:
            raise ValueError("DEALER_TEST_URL environment variable is required")
        if not self.EXCHANGE_PROD_URL:
            raise ValueError("DEALER_PROD_URL environment variable is required")
        if self.DLL_GATEWAY_REQUEST_TIMEOUT_MS <= 0:
            raise ValueError("DLL_GATEWAY_REQUEST_TIMEOUT_MS must be positive")
        if self.EXCHANGE_MODE not in ("pfcf", "simulator"):
            raise ValueError(
                f"EXCHANGE_MODE must be 'pfcf' or 'simulator', got {self.EXCHANGE_MODE!r}"
            )

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]
