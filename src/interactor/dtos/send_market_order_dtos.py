""" Module for CreateMarketOrder Dtos
"""

from dataclasses import dataclass

from src.domain.value_objects import OrderOperation, TimeInForce, OpenClose, DayTrade, OrderTypeEnum
from src.infrastructure.services.enum_converter import EnumConverter


@dataclass
class SendMarketOrderInputDto:
    """ Data Transfer Object for creating market order"""
    order_account: str
    item_code: str
    side: OrderOperation
    order_type: OrderTypeEnum
    price: float
    quantity: int
    open_close: OpenClose
    note: str
    day_trade: DayTrade = DayTrade.No
    time_in_force: TimeInForce = TimeInForce.IOC

    def to_dict(self):
        """ Convert data into dictionary and convert enum to string
        """
        return {
            "order_account": self.order_account,
            "item_code": self.item_code,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "price": self.price,
            "quantity": self.quantity,
            "open_close": self.open_close.value,
            "note": self.note,
            "day_trade": self.day_trade.value,
            "time_in_force": self.time_in_force.value
        }

    def to_pfcf_dict(self, service_container):
        """Convert data into dictionary and convert enum to pfcf enum.
        
        Args:
            service_container: Service container containing exchange API.
            
        Returns:
            Dictionary with PFCF-compatible field names and values.
        """
        converter = EnumConverter(service_container.exchange_api)
        return {
            "ACTNO": self.order_account,
            "PRODUCTID": self.item_code,
            "BS": converter.to_pfcf_enum(self.side),
            "ORDERTYPE": converter.to_pfcf_enum(self.order_type),
            "PRICE": converter.to_pfcf_decimal(self.price),
            "ORDERQTY": self.quantity,
            "TIMEINFORCE": converter.to_pfcf_enum(self.time_in_force),
            "OPENCLOSE": converter.to_pfcf_enum(self.open_close),
            "DTRADE": converter.to_pfcf_enum(self.day_trade),
            "NOTE": self.note
        }


@dataclass
class SendMarketOrderOutputDto:
    """ Data Transfer Object for creating market order"""
    is_send_order: bool
    note: str
    order_serial: str
    error_code: str = ""
    error_message: str = ""
