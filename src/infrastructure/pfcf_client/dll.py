# Stub module for PFCF DLL - only for testing
# This is a placeholder for the proprietary DLL that cannot be included in the repo

class MockEvent:
    """Mock event handler for PFCF API"""
    def __iadd__(self, handler):
        return self

    def __isub__(self, handler):
        return self

class MockLib:
    """Mock library object with event handlers"""
    def __init__(self):
        self.OnConnected = MockEvent()
        self.OnDisconnected = MockEvent()
        self.OnReply = MockEvent()
        self.OnMatch = MockEvent()
        self.OnQueryReply = MockEvent()
        self.OnQueryMatch = MockEvent()
        self.OnMarginData = MockEvent()
        self.OnMarginError = MockEvent()
        self.OnPositionData = MockEvent()
        self.OnPositionError = MockEvent()
        self.OnUnLiquidationMainData = MockEvent()
        self.OnUnLiquidationMainError = MockEvent()

class MockPFCFAPI:
    def __init__(self):
        self.PFCloginStatus = MockEvent()
        self.PFCErrorData = MockEvent()
        self.DQuoteLib = MockLib()
        self.DTradeLib = MockLib()
        self.DAccountLib = MockLib()
        self.NoticeLib = MockLib()

class MockDTrade:
    pass

class MockDecimal:
    pass

PFCFAPI = MockPFCFAPI
DTrade = MockDTrade
Decimal = MockDecimal
