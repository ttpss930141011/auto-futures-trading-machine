"""DLL Gateway Client implementation.

This client runs in child processes and communicates with the DLL Gateway Server
through ZeroMQ REQ socket to access exchange functionality.
"""

import json
import zmq
from typing import Any, Dict, List

from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.services.dll_gateway_service_interface import (
    DllGatewayServiceInterface,
    PositionInfo,
)
from src.interactor.dtos.send_market_order_dtos import (
    SendMarketOrderInputDto,
    SendMarketOrderOutputDto,
)
from src.interactor.errors.dll_gateway_errors import (
    DllGatewayConnectionError,
    DllGatewayTimeoutError,
    DllGatewayError,
)


class DllGatewayClient(DllGatewayServiceInterface):
    """Client for accessing DLL Gateway Server through ZeroMQ.

    Implements DllGatewayServiceInterface following Dependency Inversion Principle.
    Provides high-level interface while hiding ZeroMQ communication details.
    """

    def __init__(
        self,
        server_address: str,
        logger: LoggerInterface,
        timeout_ms: int = 5000,
        retry_count: int = 3,
    ):
        """Initialize DLL Gateway Client.

        Args:
            server_address: ZeroMQ address of the DLL Gateway Server.
            logger: Logger for recording events.
            timeout_ms: Timeout for requests in milliseconds.
            retry_count: Number of retry attempts for failed requests.
        """
        self._server_address = server_address
        self._logger = logger
        self._timeout_ms = timeout_ms
        self._retry_count = retry_count

        self._context = zmq.Context()
        self._socket = None
        self._connected = False

    def _ensure_connection(self) -> None:
        """Ensure connection to DLL Gateway Server is established.

        Raises:
            DllGatewayConnectionError: If connection cannot be established.
        """
        if self._socket is None:
            try:
                self._socket = self._context.socket(zmq.REQ)
                self._socket.setsockopt(zmq.RCVTIMEO, self._timeout_ms)
                self._socket.setsockopt(zmq.SNDTIMEO, self._timeout_ms)
                self._socket.connect(self._server_address)
                self._connected = True
                self._logger.log_info(f"Connected to DLL Gateway Server at {self._server_address}")
            except Exception as e:
                self._logger.log_error(f"Failed to connect to DLL Gateway Server: {e}")
                raise DllGatewayConnectionError(f"Connection failed: {str(e)}")

    def _send_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to DLL Gateway Server with retry logic.

        Args:
            request_data: Request data to send.

        Returns:
            Response data from server.

        Raises:
            DllGatewayTimeoutError: If request times out.
            DllGatewayConnectionError: If connection fails.
            DllGatewayError: If server returns an error.
        """
        last_exception = None

        for attempt in range(self._retry_count + 1):
            try:
                self._ensure_connection()

                # Send request
                request_json = json.dumps(request_data)
                self._socket.send_string(request_json)

                # Receive response
                response_json = self._socket.recv_string()
                response_data = json.loads(response_json)

                # Check if response indicates success
                if response_data.get("success", False):
                    return response_data
                else:
                    error_msg = response_data.get("error_message", "Unknown error")
                    error_code = response_data.get("error_code", "UNKNOWN")
                    raise DllGatewayError(error_msg, error_code)

            except zmq.Again:
                last_exception = DllGatewayTimeoutError(
                    f"Request timeout after {self._timeout_ms}ms"
                )
                self._logger.log_warning(f"Request timeout on attempt {attempt + 1}")
                self._reset_connection()

            except zmq.ZMQError as e:
                last_exception = DllGatewayConnectionError(f"ZMQ error: {str(e)}")
                self._logger.log_error(f"ZMQ error on attempt {attempt + 1}: {e}")
                self._reset_connection()

            except json.JSONDecodeError as e:
                last_exception = DllGatewayError(f"Invalid JSON response: {str(e)}")
                self._logger.log_error(f"JSON decode error on attempt {attempt + 1}: {e}")

            except DllGatewayError:
                # Don't retry on server-side errors
                raise

            except Exception as e:
                last_exception = DllGatewayError(f"Unexpected error: {str(e)}")
                self._logger.log_error(f"Unexpected error on attempt {attempt + 1}: {e}")

        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise DllGatewayError("All retry attempts exhausted")

    def _reset_connection(self) -> None:
        """Reset the connection to DLL Gateway Server."""
        try:
            if self._socket:
                self._socket.close()
                self._socket = None
                self._connected = False
        except Exception as e:
            self._logger.log_error(f"Error resetting connection: {e}")

    def send_order(self, input_dto: SendMarketOrderInputDto) -> SendMarketOrderOutputDto:
        """Send a market order through the DLL Gateway.

        Args:
            input_dto: SendMarketOrderInputDto containing all necessary parameters.

        Returns:
            SendMarketOrderOutputDto: Result of the order submission.

        Raises:
            DllGatewayError: If the gateway service is unavailable.
            InvalidOrderError: If the order request is invalid.
        """
        try:
            self._logger.log_info(
                f"Sending order request: {input_dto.side.name} {input_dto.quantity} "
                f"{input_dto.item_code}"
            )

            request_data = {
                "operation": "send_order",
                "parameters": input_dto.to_dict()
            }

            response_data = self._send_request(request_data)

            # Extract data from unified response format
            order_data = response_data.get("data", {})

            # Create SendMarketOrderOutputDto from response data
            return SendMarketOrderOutputDto(
                is_send_order=order_data.get("is_send_order", False),
                note=order_data.get("note", ""),
                order_serial=order_data.get("order_serial", ""),
                error_code=order_data.get("error_code", ""),
                error_message=order_data.get("error_message", ""),
            )

        except DllGatewayError:
            raise
        except Exception as e:
            self._logger.log_error(f"Error sending order: {e}")
            raise DllGatewayError(f"Order sending failed: {str(e)}")

    def get_positions(self, account: str) -> List[PositionInfo]:
        """Get current positions for an account.

        Args:
            account: The trading account identifier.

        Returns:
            List of position information.

        Raises:
            DllGatewayError: If the gateway service is unavailable.
        """
        try:
            self._logger.log_info(f"Getting positions for account: {account}")

            request_data = {
                "operation": "get_positions",
                "parameters": {"account": account}
            }

            response_data = self._send_request(request_data)

            # Extract data from unified response format
            data = response_data.get("data", {})
            positions_data = data.get("positions", [])

            # Convert response to PositionInfo objects
            positions = []
            for pos_data in positions_data:
                positions.append(PositionInfo(
                    account=pos_data["account"],
                    item_code=pos_data["item_code"],
                    quantity=pos_data["quantity"],
                    average_price=pos_data["average_price"],
                    unrealized_pnl=pos_data["unrealized_pnl"],
                ))

            return positions

        except DllGatewayError:
            raise
        except Exception as e:
            self._logger.log_error(f"Error getting positions: {e}")
            raise DllGatewayError(f"Position query failed: {str(e)}")

    def is_connected(self) -> bool:
        """Check if the DLL gateway is connected and ready.

        Returns:
            True if connected and ready, False otherwise.
        """
        try:
            health_status = self.get_health_status()
            return health_status.get("exchange_connected", False)
        except Exception:
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the DLL gateway.

        Returns:
            Dictionary containing health status information.

        Raises:
            DllGatewayError: If health check fails.
        """
        try:
            request_data = {"operation": "health_check"}
            response_data = self._send_request(request_data)

            # Extract health status from unified response format
            health_status = response_data.get("data", {})

            return health_status

        except DllGatewayError:
            raise
        except Exception as e:
            self._logger.log_error(f"Error getting health status: {e}")
            raise DllGatewayError(f"Health check failed: {str(e)}")

    def close(self) -> None:
        """Close the connection to DLL Gateway Server."""
        try:
            if self._socket:
                self._socket.close()
                self._socket = None
                self._connected = False

            if self._context:
                self._context.term()

            self._logger.log_info("DLL Gateway Client connection closed")

        except Exception as e:
            self._logger.log_error(f"Error closing DLL Gateway Client: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
