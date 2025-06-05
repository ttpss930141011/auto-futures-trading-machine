"""OrderExecutor for handling trading signals received via ZeroMQ and executing orders.

This module is responsible for receiving serialized trading signals via ZMQ PULL socket,
 deserializing them, and converting them into actual orders using the appropriate use cases.
"""

from typing import Optional
from src.infrastructure.messaging import (
    ZmqPuller,
    deserialize,
)  # Import ZMQ Puller and deserializer

# Update import path for TradingSignal
from src.infrastructure.events.trading_signal import TradingSignal
from src.domain.value_objects import OrderOperation, OpenClose, DayTrade, TimeInForce, OrderTypeEnum
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.use_cases.send_market_order import SendMarketOrderUseCase


class OrderExecutor:
    """Executes orders based on trading signals received via ZMQ."""

    def __init__(
        self,
        signal_puller: ZmqPuller,  # Inject ZmqPuller
        send_order_use_case: SendMarketOrderUseCase,
        session_repository: SessionRepositoryInterface,
        logger: LoggerInterface,
        default_quantity: int = 1,
    ):
        """Initialize the order executor.

        Args:
            # event_dispatcher: The event dispatcher to subscribe to for trading signals
            signal_puller: The ZeroMQ puller for receiving trading signals.
            send_order_use_case: Use case for sending market orders
            session_repository: Repository for accessing session information
            logger: Logger for recording order execution events
            default_quantity: Default quantity for orders if not specified
        """
        # self.event_dispatcher = event_dispatcher
        self.signal_puller = signal_puller  # Store the puller
        self.send_order_use_case = send_order_use_case
        self.session_repository = session_repository
        self.logger = logger
        self.default_quantity = default_quantity

        # Remove subscription to trading signals
        # event_dispatcher.subscribe_event_type("TRADING_SIGNAL", self.on_trading_signal)

    # Remove on_trading_signal as it's no longer an event handler
    # def on_trading_signal(self, signal: TradingSignal):
    #     ...

    def process_received_signal(self) -> bool:
        """Attempts to receive and process one trading signal from the ZMQ puller.

        This method should be called periodically in the loop of the process
        running the OrderExecutor.

        Returns:
            bool: True if a signal was received and processed (successfully or not),
                  False if no signal was received.
        """
        serialized_signal = self.signal_puller.receive(non_blocking=True)

        if serialized_signal:
            try:
                # Deserialize the signal
                signal: TradingSignal = deserialize(serialized_signal)

                if not isinstance(signal, TradingSignal):
                    self.logger.log_warning(f"Received non-TradingSignal message: {type(signal)}")
                    return True  # Consumed a message, even if wrong type

                self.logger.log_info(
                    f"Received trading signal via ZMQ: {signal.operation.name} {signal.commodity_id} at {signal.when}"
                )

                # Get account information from session
                order_account = self.session_repository.get_order_account()
                if not order_account:
                    self.logger.log_error("Cannot execute order: No order account selected")
                    return True  # Processed signal, but failed

                self.logger.log_info(f"Using order account: {order_account}")
                self.logger.log_info(
                    f"Signal details - commodity: {signal.commodity_id}, operation: {signal.operation}"
                )

                # signal.operation is already an OrderOperation enum, use it directly
                side = signal.operation

                # Create the order input DTO
                input_dto = SendMarketOrderInputDto(
                    order_account=order_account,
                    item_code=signal.commodity_id,
                    side=signal.operation,
                    order_type=OrderTypeEnum.Market,
                    price=0,  # Market orders don't require a price
                    quantity=self.default_quantity,
                    open_close=OpenClose.AUTO,
                    note="From AFTM",  # Updated note
                    day_trade=DayTrade.No,
                    time_in_force=TimeInForce.IOC,
                )

                self.logger.log_info(
                    f"Created order DTO: account={order_account}, item={signal.commodity_id}, side={signal.operation.name}, qty={self.default_quantity}"
                )

                # Execute the order
                try:
                    result = self.send_order_use_case.execute(input_dto)
                    # Use specific fields from result if available and needed for logging
                    self.logger.log_info(
                        f"Order sent successfully via ZMQ signal. Result: {result}"
                    )

                    # Publish order submitted event if needed (would likely use ZMQ PUB/SUB here too)
                    # Example: self.order_status_publisher.publish(b"ORDER_STATUS", serialize(OrderSubmittedEvent(...)))

                except Exception as e:
                    self.logger.log_error(f"Order execution failed for ZMQ signal: {str(e)}")

                return True  # Signal processed

            except Exception as e:
                self.logger.log_error(f"Failed to deserialize or process received ZMQ message: {e}")
                # Potentially log the raw message if needed for debugging
                # self.logger.log_debug(f"Raw message: {serialized_signal!r}")
                return True  # Consumed a message, even if poison pill
        else:
            # No signal received
            return False

    # Add a close method for the puller if needed
    def close(self):
        if self.logger:
            self.logger.log_info("Closing OrderExecutor resources (ZMQ puller).")
        # self.signal_puller.close() # Puller might be shared, close at higher level
        pass
