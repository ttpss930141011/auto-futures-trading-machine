from .dll import PFCFAPI, DTrade, Decimal
from .event_handler import (
    PFCOnloginStatus,
    PFCOnErrorData,
    DQuote_OnConnected,
    DQuote_OnDisconnected,
    DTradeLib_OnReply,
    DTradeLib_OnMatch,
    DTradeLib_OnQueryReply,
    DTradeLib_OnQueryMatch,
    DAccountLib_PFCQueryMarginData,
    DAccountLib_PFCQueryMarginError,
    DAccount_OnConnected,
    DAccount_OnDisconnected,
    DAccountLib_OnPositionData,
    DAccountLib_OnPositionError,
    DAccountLib_OnUnLiquidationMainData,
    DAccountLib_OnUnLiquidationMainError,
    NoticeLib_OnConnected,
    NoticeLib_OnDisconnected,
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
        self.client.DTradeLib.OnReply += DTradeLib_OnReply
        self.client.DTradeLib.OnMatch += DTradeLib_OnMatch

        self.client.DTradeLib.OnQueryReply += DTradeLib_OnQueryReply
        self.client.DTradeLib.OnQueryMatch += DTradeLib_OnQueryMatch
        self.client.DAccountLib.OnConnected += DAccount_OnConnected
        self.client.DAccountLib.OnDisconnected += DAccount_OnDisconnected
        self.client.DAccountLib.OnMarginData += DAccountLib_PFCQueryMarginData
        self.client.DAccountLib.OnMarginError += DAccountLib_PFCQueryMarginError
        self.client.DAccountLib.OnPositionData += DAccountLib_OnPositionData
        self.client.DAccountLib.OnPositionError += DAccountLib_OnPositionError
        self.client.DAccountLib.OnUnLiquidationMainData += DAccountLib_OnUnLiquidationMainData
        self.client.DAccountLib.OnUnLiquidationMainError += DAccountLib_OnUnLiquidationMainError
        self.client.NoticeLib.OnConnected += NoticeLib_OnConnected
        self.client.NoticeLib.OnDisconnected += NoticeLib_OnDisconnected
