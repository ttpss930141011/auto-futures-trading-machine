# Basana
#
# Copyright 2022-2023 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from decimal import Decimal
import datetime

from src.infrastructure.events.event import Event


class Trade:
    def __init__(self, commodity_id: str, json: dict):
        assert json["e"] == "trade"

        #: The commodity id.
        self.commodity_id: str = commodity_id
        #: The JSON representation.
        self.json: dict = json

    @property
    def id(self) -> str:
        """The trade id."""
        return str(self.json["t"])

    @property
    def price(self) -> Decimal:
        """The price."""
        return Decimal(self.json["p"])

    @property
    def amount(self) -> Decimal:
        """The amount."""
        return Decimal(self.json["q"])

    @property
    def buy_order_id(self) -> str:
        """The buyer order id."""
        return str(self.json["b"])

    @property
    def sell_order_id(self) -> str:
        """The seller order id."""
        return str(self.json["a"])


class TradeEvent(Event):
    """An event for new trades.

    :param when: The datetime when the event occurred. It must have timezone information set.
    :param trade: The trade.
    """

    def __init__(self, when: datetime.datetime, trade: Trade):
        super().__init__(when)
        #: The trade.
        self.trade: Trade = trade
