from datetime import datetime

from src.infrastructure.events.event import Event


class Tick:
    def __init__(
            self, commodity_id: str, info_time: datetime, match_time: datetime, match_price: float,
            match_buy_cnt: int, match_sell_cnt: int, match_quantity: float, match_total_qty: float,
            match_price_data: float, match_qty_data: float
    ):
        self.commodity_id = commodity_id
        self.info_time = info_time
        self.match_time = match_time
        self.match_price = match_price
        self.match_buy_cnt = match_buy_cnt
        self.match_sell_cnt = match_sell_cnt
        self.match_quantity = match_quantity
        self.match_total_qty = match_total_qty
        self.match_price_data = match_price_data
        self.match_qty_data = match_qty_data


class TickEvent(Event):
    """An event for :class:`Bar` instances.

    :param when: The datetime when the event occurred. It must have timezone information set.
    :param bar: The bar.
    """

    def __init__(self, when: datetime, tick: Tick):
        super().__init__(when)

        #: The index.
        self.tick = tick
