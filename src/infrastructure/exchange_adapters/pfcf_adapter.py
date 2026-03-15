"""PFCF Exchange Adapter.

This adapter wraps the PFCF API client and implements the ExchangeApiInterface,
acting as a bridge between the domain layer and the PFCF-specific implementation.
"""

from typing import Any, Callable, List

from src.domain.interfaces.exchange_api import ExchangeApiInterface
from src.domain.value_objects import (
    OrderOperation,
    OrderTypeEnum,
    TimeInForce,
    OpenClose,
    DayTrade,
)
from src.infrastructure.pfcf_client.api import PFCFApi
from src.interactor.dtos.send_market_order_dtos import (
    SendMarketOrderInputDto,
    SendMarketOrderOutputDto,
)
from src.interactor.dtos.get_position_dtos import PositionDto
from src.interactor.errors.dll_gateway_errors import ExchangeApiError


class PfcfExchangeAdapter(ExchangeApiInterface):
    """Adapter implementing ExchangeApiInterface for PFCF exchange.

    This adapter wraps the PFCF API client and provides a clean interface
    to the rest of the application, hiding PFCF-specific implementation details.
    """

    def __init__(self):
        """Initialize the PFCF exchange adapter."""
        self._pfcf_api = PFCFApi()

    def connect(self, **credentials) -> bool:
        """Connect to the PFCF exchange.

        Args:
            **credentials: PFCF-specific connection credentials.

        Returns:
            True if connection successful, False otherwise.
        """
        # PFCF connection is handled through the API initialization
        # and event callbacks. For now, return True if client exists.
        return self._pfcf_api.client is not None

    def send_order(
        self,
        order_account: str,
        item_code: str,
        side: OrderOperation,
        order_type: OrderTypeEnum,
        price: float,
        quantity: int,
        open_close: OpenClose,
        note: str,
        day_trade: DayTrade,
        time_in_force: TimeInForce,
    ) -> SendMarketOrderOutputDto:
        """Send an order to the PFCF exchange.

        Args:
            order_account: Trading account identifier.
            item_code: Product/commodity code.
            side: Buy or sell operation.
            order_type: Market, limit, or market price order.
            price: Order price.
            quantity: Order quantity.
            open_close: Open or close position.
            note: Order note/reference.
            day_trade: Day trade flag.
            time_in_force: Time in force setting.

        Returns:
            SendMarketOrderOutputDto with execution result.
        """
        try:
            # Convert domain enums to PFCF enums
            pfcf_side = self._convert_order_operation(side)
            pfcf_order_type = self._convert_order_type(order_type)
            pfcf_time_in_force = self._convert_time_in_force(time_in_force)
            pfcf_open_close = self._convert_open_close(open_close)
            pfcf_day_trade = self._convert_day_trade(day_trade)
            pfcf_price = self.parse_decimal(price)

            # Create PFCF order object
            order = self._pfcf_api.trade.OrderObject()
            order.ACTNO = order_account
            order.PRODUCTID = item_code
            order.BS = pfcf_side
            order.ORDERTYPE = pfcf_order_type
            order.PRICE = pfcf_price
            order.ORDERQTY = quantity
            order.TIMEINFORCE = pfcf_time_in_force
            order.OPENCLOSE = pfcf_open_close
            order.DTRADE = pfcf_day_trade
            order.NOTE = note

            # Execute order
            order_result = self._pfcf_api.client.DTradeLib.Order(order)

            if order_result is None:
                return SendMarketOrderOutputDto(
                    is_send_order=False,
                    note="",
                    order_serial="",
                    error_code="NULL_RESULT",
                    error_message="Order execution returned None"
                )

            # Return the result
            return SendMarketOrderOutputDto(
                is_send_order=order_result.ISSEND,
                note=order_result.NOTE,
                order_serial=order_result.SEQ,
                error_code=str(order_result.ERRORCODE),
                error_message=order_result.ERRORMSG,
            )

        except Exception as e:
            raise ExchangeApiError(f"PFCF order execution error: {str(e)}")

    def get_positions(self, account: str, product_id: str = "") -> List[PositionDto]:
        """Get positions from PFCF exchange.

        Args:
            account: Trading account identifier.
            product_id: Optional product filter, empty string for all.

        Returns:
            List of position DTOs.
        """
        # This is a placeholder - the actual implementation would use
        # PFCFPositionRepository internally. For now, return empty list.
        # The repository pattern is already in place for this operation.
        return []

    def subscribe_market_data(self, commodity_id: str, callback: Callable) -> bool:
        """Subscribe to market data from PFCF exchange.

        Args:
            commodity_id: Commodity/product identifier.
            callback: Callback function for market data events.

        Returns:
            True if subscription successful, False otherwise.
        """
        try:
            # Register the callback with PFCF DQuoteLib
            if hasattr(self._pfcf_api.client, "DQuoteLib"):
                self._pfcf_api.client.DQuoteLib.OnTickDataTrade += callback
                return True
            return False
        except Exception:
            return False

    def convert_enum(self, domain_enum: Any) -> Any:
        """Convert domain enum to PFCF-specific enum.

        Args:
            domain_enum: Domain layer enumeration value.

        Returns:
            PFCF-specific enum value.
        """
        if isinstance(domain_enum, OrderOperation):
            return self._convert_order_operation(domain_enum)
        elif isinstance(domain_enum, TimeInForce):
            return self._convert_time_in_force(domain_enum)
        elif isinstance(domain_enum, OpenClose):
            return self._convert_open_close(domain_enum)
        elif isinstance(domain_enum, DayTrade):
            return self._convert_day_trade(domain_enum)
        elif isinstance(domain_enum, OrderTypeEnum):
            return self._convert_order_type(domain_enum)
        return None

    def parse_decimal(self, value: float) -> Any:
        """Parse float value to PFCF decimal format.

        Args:
            value: Float value to convert.

        Returns:
            PFCF decimal representation.
        """
        return self._pfcf_api.decimal.Parse(str(value))

    def get_client(self) -> Any:
        """Get the underlying PFCF client object.

        Returns:
            PFCF client implementation.
        """
        return self._pfcf_api.client

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for PFCF exchange events.

        Args:
            event_type: Type of event to subscribe to.
            callback: Callback function to register.
        """
        # This would map event_type to specific PFCF callbacks
        # For now, this is a placeholder for future implementation
        pass

    # Private helper methods for enum conversion
    def _convert_order_operation(self, operation: OrderOperation) -> Any:
        """Convert OrderOperation to PFCF SideEnum."""
        return {
            OrderOperation.BUY: self._pfcf_api.trade.SideEnum.Buy,
            OrderOperation.SELL: self._pfcf_api.trade.SideEnum.Sell,
        }[operation]

    def _convert_time_in_force(self, tif: TimeInForce) -> Any:
        """Convert TimeInForce to PFCF TimeInForceEnum."""
        return {
            TimeInForce.ROD: self._pfcf_api.trade.TimeInForceEnum.ROD,
            TimeInForce.IOC: self._pfcf_api.trade.TimeInForceEnum.IOC,
            TimeInForce.FOK: self._pfcf_api.trade.TimeInForceEnum.FOK,
        }[tif]

    def _convert_open_close(self, oc: OpenClose) -> Any:
        """Convert OpenClose to PFCF OpenCloseEnum."""
        return {
            OpenClose.OPEN: self._pfcf_api.trade.OpenCloseEnum.Y,
            OpenClose.CLOSE: self._pfcf_api.trade.OpenCloseEnum.N,
            OpenClose.AUTO: self._pfcf_api.trade.OpenCloseEnum.AUTO,
        }[oc]

    def _convert_day_trade(self, dt: DayTrade) -> Any:
        """Convert DayTrade to PFCF DayTradeEnum."""
        return {
            DayTrade.Yes: self._pfcf_api.trade.DayTradeEnum.Y,
            DayTrade.No: self._pfcf_api.trade.DayTradeEnum.N,
        }[dt]

    def _convert_order_type(self, order_type: OrderTypeEnum) -> Any:
        """Convert OrderTypeEnum to PFCF OrderTypeEnum."""
        return {
            OrderTypeEnum.Market: self._pfcf_api.trade.OrderTypeEnum.Market,
            OrderTypeEnum.Limit: self._pfcf_api.trade.OrderTypeEnum.Limit,
            OrderTypeEnum.MarketPrice: self._pfcf_api.trade.OrderTypeEnum.MarketPrice,
        }[order_type]

    # Property accessors for backward compatibility
    @property
    def client(self):
        """Get PFCF client for backward compatibility."""
        return self._pfcf_api.client

    @property
    def trade(self):
        """Get PFCF trade module for backward compatibility."""
        return self._pfcf_api.trade

    @property
    def decimal(self):
        """Get PFCF decimal module for backward compatibility."""
        return self._pfcf_api.decimal

    @property
    def DAccountLib(self):
        """Get PFCF DAccountLib for backward compatibility."""
        return self._pfcf_api.client.DAccountLib
