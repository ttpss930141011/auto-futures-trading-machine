"""OrderExecutor for handling trading signals and executing orders.

This module is responsible for receiving trading signals and converting them into actual orders
using the appropriate use cases.
"""
from src.infrastructure.events.dispatcher import RealtimeDispatcher
from src.infrastructure.event_sources.trading_signal import TradingSignal
from src.domain.value_objects import OrderOperation, OpenClose, DayTrade, TimeInForce, OrderTypeEnum
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.use_cases.send_market_order import SendMarketOrderUseCase


class OrderExecutor:
    """Executes orders based on trading signals."""
    
    def __init__(self, 
                 event_dispatcher: RealtimeDispatcher, 
                 send_order_use_case: SendMarketOrderUseCase,
                 session_repository: SessionRepositoryInterface,
                 logger: LoggerInterface,
                 default_quantity: int = 1):
        """Initialize the order executor.
        
        Args:
            event_dispatcher: The event dispatcher to subscribe to for trading signals
            send_order_use_case: Use case for sending market orders
            session_repository: Repository for accessing session information
            logger: Logger for recording order execution events
            default_quantity: Default quantity for orders if not specified
        """
        self.event_dispatcher = event_dispatcher
        self.send_order_use_case = send_order_use_case
        self.session_repository = session_repository
        self.logger = logger
        self.default_quantity = default_quantity
        
        # Subscribe to trading signals
        event_dispatcher.subscribe_event_type("TRADING_SIGNAL", self.on_trading_signal)
    
    def on_trading_signal(self, signal: TradingSignal):
        """Handle a trading signal event by executing the appropriate order.
        
        Args:
            signal: The trading signal containing the order details
        """
        self.logger.log_info(
            f"Received trading signal: {signal.operation.name} {signal.commodity_id}"
        )
        
        # Get account information from session
        order_account = self.session_repository.get_order_account()
        if not order_account:
            self.logger.log_error("Cannot execute order: No order account selected")
            return
            
        # Create the order input DTO
        input_dto = SendMarketOrderInputDto(
            order_account=order_account,
            item_code=signal.commodity_id,
            side=signal.operation,
            order_type=OrderTypeEnum.Market,
            price=0,  # Market orders don't require a price
            quantity=self.default_quantity,
            open_close=OpenClose.AUTO,
            note=f"Auto order from signal at {signal.when}",
            day_trade=DayTrade.No,
            time_in_force=TimeInForce.IOC
        )
        
        # Execute the order
        try:
            result = self.send_order_use_case.execute(input_dto)
            self.logger.log_info(f"Order sent successfully: {result}")
            
            # Publish order submitted event if needed
            # self.event_dispatcher.publish_event("ORDER_SUBMITTED", OrderSubmittedEvent(...))
            
        except Exception as e:
            self.logger.log_error(f"Order execution failed: {str(e)}")