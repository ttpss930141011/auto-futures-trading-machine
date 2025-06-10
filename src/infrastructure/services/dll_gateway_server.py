"""DLL Gateway Server implementation.

This server runs in the main process and provides centralized access
to the exchange DLL through ZeroMQ REP socket.
"""

import json
import threading
import time
import zmq
from typing import Any, Dict, Optional, List
from dataclasses import asdict

from src.infrastructure.pfcf_client.api import PFCFApi
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.app.cli_pfcf.config import Config
from src.interactor.dtos.send_market_order_dtos import (
    SendMarketOrderInputDto,
    SendMarketOrderOutputDto,
)
from src.interactor.interfaces.services.dll_gateway_service_interface import (
    PositionInfo,
)
from src.interactor.errors.dll_gateway_errors import (
    DllGatewayError,
    ExchangeApiError,
    InvalidOrderError,
)
from src.domain.value_objects import OrderOperation, OrderTypeEnum


class DllGatewayServer:
    """Server providing centralized DLL access through ZeroMQ.
    
    Follows Single Responsibility Principle by focusing solely on
    DLL operation delegation and ZeroMQ communication.
    """

    def __init__(
        self,
        exchange_client: PFCFApi,
        config: Config,
        logger: LoggerInterface,
        bind_address: str = "tcp://*:5557",
        request_timeout_ms: int = 5000,
    ):
        """Initialize DLL Gateway Server.
        
        Args:
            exchange_client: The exchange API client instance.
            config: Configuration object for enum conversion.
            logger: Logger for recording events.
            bind_address: ZeroMQ bind address for the server.
            request_timeout_ms: Timeout for processing requests.
        """
        self._exchange_client = exchange_client
        self._config = config
        self._logger = logger
        self._bind_address = bind_address
        self._request_timeout_ms = request_timeout_ms
        
        self._context: Optional[zmq.Context] = None
        self._socket: Optional[zmq.Socket] = None
        self._running = False
        self._server_thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        """Start the DLL Gateway Server in a background thread.
        
        Returns:
            True if server started successfully, False otherwise.
        """
        try:
            if self._running:
                self._logger.log_warning("DLL Gateway Server is already running")
                return True

            self._context = zmq.Context()
            self._socket = self._context.socket(zmq.REP)
            self._socket.bind(self._bind_address)
            
            # Set socket options for reliability
            self._socket.setsockopt(zmq.RCVTIMEO, self._request_timeout_ms)
            self._socket.setsockopt(zmq.SNDTIMEO, self._request_timeout_ms)
            
            self._running = True
            self._server_thread = threading.Thread(
                target=self._run_server, 
                name="DllGatewayServer",
                daemon=True
            )
            self._server_thread.start()
            
            self._logger.log_info(f"DLL Gateway Server started on {self._bind_address}")
            return True
            
        except Exception as e:
            self._logger.log_error(f"Failed to start DLL Gateway Server: {str(e)}")
            self._cleanup()
            return False

    def stop(self) -> None:
        """Stop the DLL Gateway Server gracefully."""
        if not self._running:
            return
            
        self._logger.log_info("Stopping DLL Gateway Server...")
        self._running = False
        
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=2.0)
            
        self._cleanup()
        self._logger.log_info("DLL Gateway Server stopped")

    def _run_server(self) -> None:
        """Main server loop for processing requests."""
        self._logger.log_info("DLL Gateway Server loop started")
        
        while self._running:
            try:
                # Receive request with timeout
                try:
                    raw_request = self._socket.recv(zmq.NOBLOCK)
                except zmq.Again:
                    time.sleep(0.001)  # Prevent busy waiting
                    continue
                
                # Process request
                response = self._process_request(raw_request)
                
                # Send response
                self._socket.send_string(json.dumps(response))
                
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break
                self._logger.log_error(f"ZMQ error in server loop: {e}")
            except Exception as e:
                self._logger.log_error(f"Unexpected error in server loop: {e}")
                # Send error response if possible
                try:
                    error_response = {
                        "success": False,
                        "error_message": "Internal server error",
                        "error_code": "INTERNAL_ERROR"
                    }
                    self._socket.send_string(json.dumps(error_response))
                except:
                    pass

    def _process_request(self, raw_request: bytes) -> Dict[str, Any]:
        """Process incoming request and return response.
        
        Args:
            raw_request: Raw request bytes from ZeroMQ.
            
        Returns:
            Response dictionary.
        """
        try:
            # Parse request
            request_data = json.loads(raw_request.decode('utf-8'))
            operation = request_data.get("operation")
            
            self._logger.log_info(f"Processing DLL Gateway request: {operation}")
            
            # Route to appropriate handler
            if operation == "send_order":
                return self._handle_send_order(request_data)
            elif operation == "get_positions":
                return self._handle_get_positions(request_data)
            elif operation == "health_check":
                return self._handle_health_check()
            else:
                return {
                    "success": False,
                    "error_message": f"Unknown operation: {operation}",
                    "error_code": "UNKNOWN_OPERATION"
                }
                
        except json.JSONDecodeError as e:
            self._logger.log_error(f"Invalid JSON in request: {e}")
            return {
                "success": False,
                "error_message": "Invalid JSON format",
                "error_code": "INVALID_JSON"
            }
        except Exception as e:
            self._logger.log_error(f"Error processing request: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "error_code": "PROCESSING_ERROR"
            }

    def _handle_send_order(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send order request.
        
        Args:
            request_data: Request data containing order parameters.
            
        Returns:
            Order response dictionary.
        """
        try:
            # Extract order parameters
            order_params = request_data.get("parameters", {})
            
            # Validate required parameters
            required_fields = [
                "order_account", "item_code", "side", "order_type",
                "price", "quantity", "open_close", "note", 
                "day_trade", "time_in_force"
            ]
            
            missing_fields = [field for field in required_fields 
                            if field not in order_params]
            if missing_fields:
                raise InvalidOrderError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Create SendMarketOrderInputDto from the request parameters
            # We need to convert string values back to enums
            from src.domain.value_objects import OrderOperation, OrderTypeEnum, OpenClose, DayTrade, TimeInForce
            
            input_dto = SendMarketOrderInputDto(
                order_account=order_params["order_account"],
                item_code=order_params["item_code"],
                side=OrderOperation(order_params["side"]) if isinstance(order_params["side"], str) else order_params["side"],
                order_type=OrderTypeEnum(order_params["order_type"]) if isinstance(order_params["order_type"], str) else order_params["order_type"],
                price=float(order_params["price"]),
                quantity=int(order_params["quantity"]),
                open_close=OpenClose(order_params["open_close"]) if isinstance(order_params["open_close"], str) else order_params["open_close"],
                note=order_params["note"],
                day_trade=DayTrade(order_params["day_trade"]) if isinstance(order_params["day_trade"], str) else order_params["day_trade"],
                time_in_force=TimeInForce(order_params["time_in_force"]) if isinstance(order_params["time_in_force"], str) else order_params["time_in_force"],
            )
            
            # Execute order through exchange API
            response = self._execute_order(input_dto)
            
            self._logger.log_info(
                f"Order executed: {input_dto.side.name} {input_dto.quantity} "
                f"{input_dto.item_code} - Success: {response.is_send_order}"
            )
            
            return asdict(response)
            
        except InvalidOrderError as e:
            self._logger.log_error(f"Invalid order request: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "error_code": "INVALID_ORDER"
            }
        except Exception as e:
            self._logger.log_error(f"Error executing order: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "error_code": "ORDER_EXECUTION_ERROR"
            }

    def _execute_order(self, input_dto: SendMarketOrderInputDto) -> SendMarketOrderOutputDto:
        """Execute order using exchange DLL.
        
        Args:
            input_dto: The order input DTO to execute.
            
        Returns:
            SendMarketOrderOutputDto with execution result.
        """
        try:
            # Convert to PFCF format using the existing method
            pfcf_input = input_dto.to_pfcf_dict(self._config)

            # Use the correct DLL API pattern matching send_market_order.py
            order = self._exchange_client.trade.OrderObject()
            order.ACTNO = pfcf_input.get("ACTNO")
            order.PRODUCTID = pfcf_input.get("PRODUCTID")
            order.BS = pfcf_input.get("BS")
            order.ORDERTYPE = pfcf_input.get("ORDERTYPE")
            order.PRICE = pfcf_input.get("PRICE")
            order.ORDERQTY = pfcf_input.get("ORDERQTY")
            order.TIMEINFORCE = pfcf_input.get("TIMEINFORCE")
            order.OPENCLOSE = pfcf_input.get("OPENCLOSE")
            order.DTRADE = pfcf_input.get("DTRADE")
            order.NOTE = pfcf_input.get("NOTE")

            # Execute order using the correct API (same as send_market_order.py)
            order_result = self._exchange_client.client.DTradeLib.Order(order)
            
            if order_result is None:
                return SendMarketOrderOutputDto(
                    is_send_order=False,
                    note="",
                    order_serial="",
                    error_code="NULL_RESULT",
                    error_message="Order execution returned None"
                )

            # Return the result in the same format as send_market_order.py
            return SendMarketOrderOutputDto(
                is_send_order=order_result.ISSEND,
                note=order_result.NOTE,
                order_serial=order_result.SEQ,
                error_code=str(order_result.ERRORCODE),
                error_message=order_result.ERRORMSG,
            )
                
        except Exception as e:
            self._logger.log_error(f"Exchange API error: {e}")
            raise ExchangeApiError(f"Exchange API error: {str(e)}")

    def _handle_get_positions(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get positions request.
        
        Args:
            request_data: Request data containing account parameter.
            
        Returns:
            Positions response dictionary.
        """
        try:
            account = request_data.get("parameters", {}).get("account")
            if not account:
                return {
                    "success": False,
                    "error_message": "Account parameter is required",
                    "error_code": "MISSING_ACCOUNT"
                }
            
            # Query positions through exchange API
            positions = self._get_account_positions(account)
            
            return {
                "success": True,
                "positions": [asdict(pos) for pos in positions]
            }
            
        except Exception as e:
            self._logger.log_error(f"Error getting positions: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "error_code": "POSITION_QUERY_ERROR"
            }

    def _get_account_positions(self, account: str) -> List[PositionInfo]:
        """Get positions for an account using exchange DLL.
        
        Args:
            account: The trading account identifier.
            
        Returns:
            List of position information.
        """
        try:
            # Query positions through exchange API
            # This is a placeholder - actual implementation depends on DLL API
            positions = []
            
            # Note: Actual implementation would call DLL methods like:
            # position_data = self._exchange_client.client.DAccountLib.QueryPosition(account)
            # Then parse the response and create PositionInfo objects
            
            return positions
            
        except Exception as e:
            self._logger.log_error(f"Error querying positions from exchange: {e}")
            raise ExchangeApiError(f"Position query error: {str(e)}")

    def _handle_health_check(self) -> Dict[str, Any]:
        """Handle health check request.
        
        Returns:
            Health status dictionary.
        """
        try:
            # Check exchange client connectivity
            is_connected = self._exchange_client.client is not None
            
            return {
                "success": True,
                "status": "healthy" if is_connected else "unhealthy",
                "exchange_connected": is_connected,
                "timestamp": int(time.time()),
                "server_running": self._running
            }
            
        except Exception as e:
            self._logger.log_error(f"Error in health check: {e}")
            return {
                "success": False,
                "status": "unhealthy",
                "error_message": str(e),
                "error_code": "HEALTH_CHECK_ERROR"
            }

    def _cleanup(self) -> None:
        """Clean up server resources."""
        try:
            if self._socket:
                self._socket.close()
                self._socket = None
                
            if self._context:
                self._context.term()
                self._context = None
                
        except Exception as e:
            self._logger.log_error(f"Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()