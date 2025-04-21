from .dll import PFCFAPI, DTrade, Decimal
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
