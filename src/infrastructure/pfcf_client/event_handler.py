""" PFC events """

from src.interactor.errors.error_classes import LoginFailedException

# Global variable to store login status
_login_status = None


def PFCOnloginStatus(status):
    """Handle login status updates"""
    global _login_status
    print(f"Login status: {status}")
    _login_status = status

    # Check if status contains error message
    if "錯誤" in status or "error" in status.lower():
        raise LoginFailedException(status)


def PFCOnErrorData(msg):
    """Handle error messages"""
    raise Exception(msg)


""" DAccount events """


def DAccount_OnConnected():
    print("內期帳務連線")
    return


def DAccount_OnDisconnected():
    print("內期帳務斷線")
    return


def DAccountLib_PFCQueryMarginData(
    EXRATE,
    LCTDAB,
    LTDAB,
    DWAMT,
    OSPRTLOS,
    PRTLOS,
    OPTOSPRTLOS,
    OPTPRTLOS,
    TPREMIUM,
    ORIGNFEE,
    CTAXAMT,
    ORDPREMIUM,
    CTDAB,
    ORDIAMT,
    IAMT,
    MAMT,
    ORDCEXCESS,
    BPREMIUM,
    SPREMIUM,
    OPTEQUITY,
    INIRATE,
    MATRATE,
    OPTRATE,
    TWDOPTEQUITY,
    TWDINIRATE,
    TWDORDEXCESS,
    TMP1PRICES,
    EXCERCISEPRICE,
    SYSDATE,
    SYSTIME,
    ACCOUNTNO,
):
    print(
        "匯率 %s"
        "\t昨日權益數 %s"
        "\t昨日餘額 %s"
        "\t存提 %s"
        "\t本日期貨平倉損益淨額 %s"
        "\t未沖銷期貨浮動損益 %s"
        "\t選擇權平倉損益 %s"
        "\t選擇權未平倉浮動損益 %s"
        "\t權利金收入與支出 %s"
        "\t手續費 %s"
        "\t期交稅 %s"
        "\t委託權利金 %s"
        "\t權益數 %s"
        "\t委託保證金 %s"
        "\t原始保證金 %s"
        "\t維持保證金 %s"
        "\t可動用（出金）保證金 %s"
        "\t 未沖銷買方權利金市值 %s"
        "\t未沖銷賣方權利金市值 %s"
        "\t權益總值 %s"
        "\t原始比率 %s"
        "\t維持比率 %s"
        "\t風險指標 %s"
        "\t台幣權益總值 %s"
        "\t台幣原始比率 %s"
        "\t台幣下單可用保證金 %s"
        "\t依「加收保證金指標」所加收之保證金 %s"
        "\t到期履約損益 %s"
        "\t資料更新日期 %s"
        "\t資料更新時間 %s"
        "\t帳號 %s"
        % (
            EXRATE,
            LCTDAB,
            LTDAB,
            DWAMT,
            OSPRTLOS,
            PRTLOS,
            OPTOSPRTLOS,
            OPTPRTLOS,
            TPREMIUM,
            ORIGNFEE,
            CTAXAMT,
            ORDPREMIUM,
            CTDAB,
            ORDIAMT,
            IAMT,
            MAMT,
            ORDCEXCESS,
            BPREMIUM,
            SPREMIUM,
            OPTEQUITY,
            INIRATE,
            MATRATE,
            OPTRATE,
            TWDOPTEQUITY,
            TWDINIRATE,
            TWDORDEXCESS,
            TMP1PRICES,
            EXCERCISEPRICE,
            SYSDATE,
            SYSTIME,
            ACCOUNTNO,
        )
    )

    return


def DAccountLib_PFCQueryMarginError(_ERRORCODE, ERRORMESSAGE):
    print("內期查詢保證金發生錯誤: %s" % ERRORMESSAGE)
    return


def DAccountLib_OnPositionData(
    count,
    recordno,
    investorAcno,
    ProductId,
    productKind,
    OTQtyB,
    OTQtyS,
    NowOrderQtyB,
    NowOrderQtyS,
    NowMatchQtyB,
    NowMatchQtyS,
    TodayEnd,
    NowOTQtyB,
    NowOTQtyS,
    RealPrice,
    AvgCostB,
    AvgCostS,
    PriceDiffB,
    PriceDiffS,
    PricePL,
    Curren,
    LiquidationPL,
):
    print(
        "筆數 %s"
        "\t目前第幾筆 %s"
        "\t帳號 %s"
        "\t商品代碼 %s"
        "\t商品種類 %s"
        "\t昨日買進留倉 %s"
        "\t昨日賣出留倉 %s"
        "\t今日委託買進 %s"
        "\t今日委託賣出 %s"
        "\t今日成交買進 %s"
        "\t今日成交賣出 %s"
        "\t本日了結 %s"
        "\t目前買進留倉 %s"
        "\t目前賣出留倉 %s"
        "\t參考即時價 %s"
        "\t買進平均成交價 %s"
        "\t賣出平均成交價 %s"
        "\t價差買 %s"
        "\t價差賣 %s"
        "\t未平倉損益 %s"
        "\t幣別 %s"
        "\t平倉損益 %s"
        % (
            count,
            recordno,
            investorAcno,
            ProductId,
            productKind,
            OTQtyB,
            OTQtyS,
            NowOrderQtyB,
            NowOrderQtyS,
            NowMatchQtyB,
            NowMatchQtyS,
            TodayEnd,
            NowOTQtyB,
            NowOTQtyS,
            RealPrice,
            AvgCostB,
            AvgCostS,
            PriceDiffB,
            PriceDiffS,
            PricePL,
            Curren,
            LiquidationPL,
        )
    )


def DAccountLib_OnPositionError(ERRORCODE, MESSAGE):
    print("OnDAccountOnPositionError %s %s" % (ERRORCODE, MESSAGE))


def DAccountLib_OnUnLiquidationMainData(
    count,
    recordno,
    investorAcno,
    BS,
    ProductId,
    TotalOTQTY,
    RefTotalPrice,
    RefTotalPL,
    AvgMatchPrice,
    _productKind,
    Curren,
    RealPrice,
    multiplecomno,
    multipleBS,
    multipleMatchPrice1,
    multipleMatchPrice2,
    PriceDiff,
    MultiName,
):
    print(
        "筆數 %s"
        "\t目前第幾筆 %s"
        "\t帳號 %s"
        "\t買賣別 %s"
        "\t商品代碼 %s"
        "\t未平倉口數 %s"
        "\t參考現值 %s"
        "\t參考浮動損益 %s"
        "\t平均成交價 %s"
        "\t幣別 %s"
        "\t參考即時價 %s"
        "\t複式商品代碼 %s"
        "\t複式買賣別 %s"
        "\t複式第1隻腳價格 %s"
        "\t複式第2隻腳價格 %s"
        "\t價差 %s"
        "\t複式種類 %s"
        % (
            count,
            recordno,
            investorAcno,
            BS,
            ProductId,
            TotalOTQTY,
            RefTotalPrice,
            RefTotalPL,
            AvgMatchPrice,
            Curren,
            RealPrice,
            multiplecomno,
            multipleBS,
            multipleMatchPrice1,
            multipleMatchPrice2,
            PriceDiff,
            MultiName,
        )
    )


def DAccountLib_OnUnLiquidationMainError(ERRORCODE, MESSAGE):
    print("OnDAccountOnUnLiquidationMainError %s %s" % (ERRORCODE, MESSAGE))


""" DTrade events """


def DTrade_OnDisconnected():
    print("內期交易斷線")
    return


def DTrade_OnConnected():
    print("內期交易連線")
    return


def DTradeLib_OnReply(reply):
    print(
        "委回收到 委託書號%s 資料: %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
        % (
            reply.orderNo,
            reply.investorAcno,
            reply.orderTime,
            reply.BS,
            reply.productId,
            reply.matchQty,
            reply.NoMatchQty,
            reply.DelQty,
            reply.orderStatus,
            reply.Statuscode,
            reply.netWorkId,
            reply.orderPrice,
            reply.orderQty,
            reply.OpenOffSetFlag,
            reply.OrderCondition,
            reply.dtrade,
            reply.mdate,
            reply.productKind,
            reply.sourcetype,
            reply.note,
            reply.seq,
            reply.tradedate,
            reply.ORDERKIND,
            reply.ORDERTYPE,
            reply.LastMatchPrice,
            reply.LastMatchQty,
            reply.LastMatchseq,
        )
    )
    return


def DTradeLib_OnMatch(match):
    print(
        "成回收到:%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
        % (
            match.investorAcno,
            match.orderNo,
            match.matchTime,
            match.BS,
            match.productId,
            match.MatchPrice,
            match.MatchQty,
            match.netWorkId,
            match.productKind,
            match.matchseq,
            match.matchpricefoot1,
            match.matchpricefoot2,
            match.note,
            match.tradedate,
            match.ORDERKIND,
        )
    )


def DTradeLib_OnQueryReply(count, recordno, reply):
    print(
        "查詢委回結果:%s %s %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
        % (
            count,
            recordno,
            reply.investorAcno,
            reply.orderNo,
            reply.orderTime,
            reply.BS,
            reply.productId,
            reply.matchQty,
            reply.NoMatchQty,
            reply.DelQty,
            reply.orderStatus,
            reply.Statuscode,
            reply.netWorkId,
            reply.orderPrice,
            reply.orderQty,
            reply.OpenOffSetFlag,
            reply.OrderCondition,
            reply.dtrade,
            reply.mdate,
            reply.productKind,
            reply.sourcetype,
            reply.note,
            reply.seq,
            reply.tradedate,
            reply.ORDERKIND,
            reply.ORDERTYPE,
            reply.LastMatchPrice,
            reply.LastMatchQty,
            reply.LastMatchseq,
        )
    )


def DTradeLib_OnQueryMatch(count, recordno, match):
    print(
        "查詢成回結果:%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
        % (
            count,
            recordno,
            match.investorAcno,
            match.orderNo,
            match.matchTime,
            match.BS,
            match.productId,
            match.MatchPrice,
            match.MatchQty,
            match.netWorkId,
            match.productKind,
            match.matchseq,
            match.matchpricefoot1,
            match.matchpricefoot2,
            match.note,
            match.tradedate,
            match.ORDERKIND,
        )
    )


""" DQuote events """


def DQuote_OnDisconnected():
    print("內期報價斷線")
    return


def DQuote_OnConnected():
    print("內期報價連線")
    return


def DQuote_OnTickDataTrade(
    COMMODITYID,
    InfoTime,
    MatchTime,
    MatchPrice,
    MatchBuyCnt,
    MatchSellCnt,
    MatchQuantity,
    MatchTotalQty,
    MatchPriceData,
    MatchQtyData,
):
    print(
        "內期成交價報價 %s,%s,%s,%s,%s,%s,%s,%s"
        % (
            COMMODITYID,
            InfoTime,
            MatchTime,
            MatchPrice,
            MatchBuyCnt,
            MatchSellCnt,
            MatchQuantity,
            MatchTotalQty,
        )
    )
    # client.DQuoteLib.UnRegItem(PRODUCTID)
    # client.DQuoteLib.OnTickDataTrade -= DQuote_OnTickDataTrade
    return MatchPriceData, MatchQtyData


def DQuote_OnTickDataBidOffer(
    COMMODITYID,
    BP1,
    BP2,
    BP3,
    BP4,
    BP5,
    BQ1,
    BQ2,
    BQ3,
    BQ4,
    BQ5,
    SP1,
    SP2,
    SP3,
    SP4,
    SP5,
    SQ1,
    SQ2,
    SQ3,
    SQ4,
    SQ5,
):
    print(
        "五檔報價 %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
        % (
            COMMODITYID,
            BP1,
            BP2,
            BP3,
            BP4,
            BP5,
            BQ1,
            BQ2,
            BQ3,
            BQ4,
            BQ5,
            SP1,
            SP2,
            SP3,
            SP4,
            SP5,
            SQ1,
            SQ2,
            SQ3,
            SQ4,
            SQ5,
        )
    )
    # client.DQuoteLib.OnTickDataBidOffer -= DQuote_OnTickDataBidOffer
    return True


def DQuote_OnTickDataBeforeTrade(
    COMMODITYID,
    InfoTime,
    MatchTime,
    MatchPrice,
    MatchBuyCnt,
    MatchSellCnt,
    MatchQuantity,
    MatchTotalQty,
    MatchPriceData,
    MatchQtyData,
):
    print(
        "盤前試搓 %s,%s,%s,%s,%s,%s,%s,%s"
        % (
            COMMODITYID,
            InfoTime,
            MatchTime,
            MatchPrice,
            MatchBuyCnt,
            MatchSellCnt,
            MatchQuantity,
            MatchTotalQty,
        )
    )
    # client.DQuoteLib.UnRegItem(PRODUCTID)
    # client.DQuoteLib.OnTickDataTrade -= DQuote_OnTickDataTrade
    return MatchPriceData, MatchQtyData


def DQuote_OnTickDataBeforeBidOffer(
    COMMODITYID,
    BP1,
    BP2,
    BP3,
    BP4,
    BP5,
    BQ1,
    BQ2,
    BQ3,
    BQ4,
    BQ5,
    SP1,
    SP2,
    SP3,
    SP4,
    SP5,
    SQ1,
    SQ2,
    SQ3,
    SQ4,
    SQ5,
):
    print(
        "盤前試搓五檔 %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
        % (
            COMMODITYID,
            BP1,
            BP2,
            BP3,
            BP4,
            BP5,
            BQ1,
            BQ2,
            BQ3,
            BQ4,
            BQ5,
            SP1,
            SP2,
            SP3,
            SP4,
            SP5,
            SQ1,
            SQ2,
            SQ3,
            SQ4,
            SQ5,
        )
    )
    # client.DQuoteLib.OnTickDataBidOffer -= DQuote_OnTickDataBidOffer
    return True


""" Notice events """


def NoticeLib_OnDisconnected():
    return


def NoticeLib_OnConnected():
    print("訊息平台連線成功")
    return
