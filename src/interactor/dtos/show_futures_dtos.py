from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FutureDataDto:
    commodity_id: str
    product_name: str
    underlying_id: str
    delivery_month: str
    market_code: str
    position_price: str
    expiration_date: str
    max_price: float = 0.0
    min_price: float = 0.0
    # Add any other fields that might be relevant


@dataclass
class ShowFuturesInputDto:
    account: str
    futures_code: str = ""


@dataclass
class ShowFuturesOutputDto:
    success: bool
    message: str
    futures_data: List[FutureDataDto] = None 