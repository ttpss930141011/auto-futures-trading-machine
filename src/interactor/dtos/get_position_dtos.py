"""
Data Transfer Objects for the GetPosition use case.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PositionDto:
    """A single position record."""

    investor_account: str
    product_id: str
    product_kind: Optional[int] = None
    yesterday_long: Optional[int] = None
    yesterday_short: Optional[int] = None
    today_order_long: Optional[int] = None
    today_order_short: Optional[int] = None
    today_filled_long: Optional[int] = None
    today_filled_short: Optional[int] = None
    today_closed: Optional[int] = None
    current_long: Optional[int] = None
    current_short: Optional[int] = None
    reference_price: Optional[float] = None
    avg_cost_long: Optional[float] = None
    avg_cost_short: Optional[float] = None
    unrealized_pl: Optional[float] = None
    currency: Optional[str] = None
    realized_pl: Optional[float] = None

    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # 確保必要欄位不為空
        if not self.investor_account:
            raise ValueError("investor_account cannot be empty")
        if not self.product_id:
            raise ValueError("product_id cannot be empty")

        # 設置預設值
        if self.product_kind is None:
            self.product_kind = 0
        if self.yesterday_long is None:
            self.yesterday_long = 0
        if self.yesterday_short is None:
            self.yesterday_short = 0
        if self.today_order_long is None:
            self.today_order_long = 0
        if self.today_order_short is None:
            self.today_order_short = 0
        if self.today_filled_long is None:
            self.today_filled_long = 0
        if self.today_filled_short is None:
            self.today_filled_short = 0
        if self.today_closed is None:
            self.today_closed = 0
        if self.current_long is None:
            self.current_long = 0
        if self.current_short is None:
            self.current_short = 0
        if self.reference_price is None:
            self.reference_price = 0.0
        if self.avg_cost_long is None:
            self.avg_cost_long = 0.0
        if self.avg_cost_short is None:
            self.avg_cost_short = 0.0
        if self.unrealized_pl is None:
            self.unrealized_pl = 0.0
        if self.currency is None:
            self.currency = ""
        if self.realized_pl is None:
            self.realized_pl = 0.0

    @property
    def net_position(self) -> int:
        """Calculate net position (long - short)."""
        return self.current_long - self.current_short

    @property
    def has_position(self) -> bool:
        """Check if there's any current position."""
        return self.current_long > 0 or self.current_short > 0

    @property
    def total_unrealized_pl(self) -> float:
        """Get total unrealized P&L."""
        return self.unrealized_pl

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "investor_account": self.investor_account,
            "product_id": self.product_id,
            "product_kind": self.product_kind,
            "yesterday_long": self.yesterday_long,
            "yesterday_short": self.yesterday_short,
            "today_order_long": self.today_order_long,
            "today_order_short": self.today_order_short,
            "today_filled_long": self.today_filled_long,
            "today_filled_short": self.today_filled_short,
            "today_closed": self.today_closed,
            "current_long": self.current_long,
            "current_short": self.current_short,
            "reference_price": self.reference_price,
            "avg_cost_long": self.avg_cost_long,
            "avg_cost_short": self.avg_cost_short,
            "unrealized_pl": self.unrealized_pl,
            "currency": self.currency,
            "realized_pl": self.realized_pl,
            "net_position": self.net_position,
            "has_position": self.has_position,
        }


@dataclass
class GetPositionInputDto:
    """Input data for GetPositionUseCase."""

    order_account: str
    product_id: str = ""  # empty string for all products

    def __post_init__(self):
        """Validate input data."""
        if not self.order_account:
            raise ValueError("order_account cannot be empty")


@dataclass
class GetPositionOutputDto:
    """Output data from GetPositionUseCase."""

    positions: List[PositionDto]
    error: Optional[str] = None
    total_positions: int = 0

    def __post_init__(self):
        """Calculate derived fields."""
        if self.positions:
            self.total_positions = len(self.positions)

    @property
    def has_error(self) -> bool:
        """Check if there's an error."""
        return self.error is not None

    @property
    def is_empty(self) -> bool:
        """Check if no positions were found."""
        return len(self.positions) == 0 and not self.has_error

    @property
    def positions_with_holdings(self) -> List[PositionDto]:
        """Get only positions that have current holdings."""
        return [pos for pos in self.positions if pos.has_position]

    def get_positions_by_product(self, product_id: str) -> List[PositionDto]:
        """Get positions for a specific product."""
        return [pos for pos in self.positions if pos.product_id == product_id]
