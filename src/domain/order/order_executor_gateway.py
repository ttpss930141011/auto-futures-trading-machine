"""OrderExecutor with DLL Gateway integration.

This version of OrderExecutor uses the DLL Gateway Client to communicate
with the centralized DLL Gateway Server, eliminating the need for
duplicate DLL instances in child processes.
"""

from typing import Optional
from src.infrastructure.messaging import (
    ZmqPuller,
    deserialize,
)
from src.infrastructure.events.trading_signal import TradingSignal
from src.domain.value_objects import OrderOperation, OpenClose, DayTrade, TimeInForce, OrderTypeEnum
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.dll_gateway_service_interface import (
    DllGatewayServiceInterface,
)
from src.interactor.dtos.send_market_order_dtos import SendMarketOrderInputDto
from src.interactor.errors.dll_gateway_errors import DllGatewayError


class OrderExecutorGateway:
    """Executes orders using DLL Gateway Service.

    This class follows Single Responsibility Principle by focusing solely on
    processing trading signals and delegating order execution to the gateway service.
    Follows Dependency Inversion Principle by depending on DllGatewayServiceInterface.
    """

    def __init__(
        self,
        signal_puller: ZmqPuller,
        dll_gateway_service: DllGatewayServiceInterface,
        session_repository: SessionRepositoryInterface,
        logger: LoggerInterface,
        default_quantity: int = 1,
    ):
        """Initialize the order executor with gateway integration.

        Args:
            signal_puller: The ZeroMQ puller for receiving trading signals.
            dll_gateway_service: Service for communicating with DLL Gateway.
            session_repository: Repository for accessing session information.
            logger: Logger for recording order execution events.
            default_quantity: Default quantity for orders if not specified.
        """
        self._signal_puller = signal_puller
        self._dll_gateway_service = dll_gateway_service
        self._session_repository = session_repository
        self._logger = logger
        self._default_quantity = default_quantity

    def process_received_signal(self) -> bool:
        """Attempts to receive and process one trading signal from the ZMQ puller.

        This method should be called periodically in the loop of the process
        running the OrderExecutor.

        Returns:
            bool: True if a signal was received and processed (successfully or not),
                  False if no signal was received.
        """
        serialized_signal = self._signal_puller.receive(non_blocking=True)

        if serialized_signal:
            try:
                # Deserialize the signal
                signal: TradingSignal = deserialize(serialized_signal)

                if not isinstance(signal, TradingSignal):
                    self._logger.log_warning(f"Received non-TradingSignal message: {type(signal)}")
                    return True  # Consumed a message, even if wrong type

                self._logger.log_info(
                    f"Received trading signal via ZMQ: {signal.operation.name} {signal.commodity_id} at {signal.when}"
                )

                # Process the trading signal
                self._process_trading_signal(signal)

                return True  # Signal processed

            except Exception as e:
                self._logger.log_error(f"Failed to deserialize or process received ZMQ message: {e}")
                return True  # Consumed a message, even if poison pill
        else:
            # No signal received
            return False

    def _process_trading_signal(self, signal: TradingSignal) -> None:
        """Process a trading signal and execute the corresponding order.

        Args:
            signal: The trading signal to process.
        """
        try:
            # Get account information from session
            order_account = self._session_repository.get_order_account()
            if not order_account:
                self._logger.log_error("Cannot execute order: No order account selected")
                return

            self._logger.log_info(f"Using order account: {order_account}")
            self._logger.log_info(
                f"Signal details - commodity: {signal.commodity_id}, operation: {signal.operation}"
            )

            # Create order input DTO for DLL Gateway
            input_dto = self._create_order_input_dto(signal, order_account)

            # Execute order through DLL Gateway
            self._execute_order_via_gateway(input_dto)

        except Exception as e:
            self._logger.log_error(f"Error processing trading signal: {e}")

    def _create_order_input_dto(self, signal: TradingSignal, order_account: str) -> SendMarketOrderInputDto:
        """Create an order input DTO from trading signal.

        Args:
            signal: The trading signal.
            order_account: The order account to use.

        Returns:
            SendMarketOrderInputDto object ready for gateway execution.
        """
        return SendMarketOrderInputDto(
            order_account=order_account,
            item_code=signal.commodity_id,
            side=signal.operation,  # Use the enum directly
            order_type=OrderTypeEnum.Market,
            price=0.0,  # Market orders don't require a price
            quantity=self._default_quantity,
            open_close=OpenClose.AUTO,
            note="From AFTM Gateway",
            day_trade=DayTrade.No,
            time_in_force=TimeInForce.IOC,
        )

    def _execute_order_via_gateway(self, input_dto: SendMarketOrderInputDto) -> None:
        """Execute order through DLL Gateway Service.

        Args:
            input_dto: The order input DTO to execute.
        """
        try:
            self._logger.log_info(
                f"Sending order to DLL Gateway: {input_dto.side.name} {input_dto.quantity} "
                f"{input_dto.item_code}"
            )

            # Check gateway connection before executing
            if not self._dll_gateway_service.is_connected():
                self._logger.log_error("DLL Gateway is not connected")
                return

            # Execute order through gateway
            response = self._dll_gateway_service.send_order(input_dto)

            if response.is_send_order:
                self._logger.log_info(
                    f"Order executed successfully via DLL Gateway. "
                    f"Order Serial: {response.order_serial}"
                )
            else:
                self._logger.log_error(
                    f"Order execution failed via DLL Gateway. "
                    f"Error: {response.error_message} (Code: {response.error_code})"
                )

        except DllGatewayError as e:
            self._logger.log_error(f"DLL Gateway error during order execution: {e}")
        except Exception as e:
            self._logger.log_error(f"Unexpected error during order execution: {e}")

    def get_health_status(self) -> dict:
        """Get health status including gateway connectivity.

        Returns:
            Dictionary containing health status information.
        """
        try:
            gateway_status = self._dll_gateway_service.get_health_status()
            return {
                "order_executor_running": True,
                "gateway_status": gateway_status,
                "signal_puller_active": self._signal_puller is not None,
            }
        except Exception as e:
            self._logger.log_error(f"Error getting health status: {e}")
            return {
                "order_executor_running": True,
                "gateway_status": {"status": "unhealthy", "error": str(e)},
                "signal_puller_active": self._signal_puller is not None,
            }

    def close(self) -> None:
        """Close the order executor and cleanup resources."""
        try:
            self._logger.log_info("Closing OrderExecutorGateway resources")

            # Close DLL Gateway connection
            if hasattr(self._dll_gateway_service, 'close'):
                self._dll_gateway_service.close()

        except Exception as e:
            self._logger.log_error(f"Error during OrderExecutorGateway cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
