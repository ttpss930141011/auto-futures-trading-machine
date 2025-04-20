import asyncio
from typing import Callable

# Relative imports should still work from within the same package
from .dll import PFCFAPI, DTrade, Decimal
from ..events.tick import TickEvent  # Assuming events is one level up from infrastructure
from ...interactor.errors.error_classes import LoginFailedException
from .event_handler import (
    PFCOnloginStatus,
    PFCOnErrorData,
    DQuote_OnConnected,
    DQuote_OnDisconnected,
)


class PFCFApi:
    """PFCF API client for futures trading"""

    def __init__(self):
        self.client = PFCFAPI()
        self.trade = DTrade
        self.decimal = Decimal
        self.client.PFCloginStatus += PFCOnloginStatus
        self.client.PFCErrorData += PFCOnErrorData
        self.client.DQuoteLib.OnConnected += DQuote_OnConnected
        self.client.DQuoteLib.OnDisconnected += DQuote_OnDisconnected
        # Commented out event handlers remain here
        # self.client.DQuoteLib.OnTickDataTrade += DQuote_OnTickDataTrade
        # ... (keep all other commented out lines) ...
        # self.client.NoticeLib.OnDisconnected += NoticeLib_OnDisconnected

    @property
    def login_status(self):
        """Get the current login status"""
        # This import needs to remain relative to the event_handler module in the same directory
        from .event_handler import _login_status

        return _login_status
