"""Send Market Order Use Case V2 - Using abstracted exchange API."""

from typing import Dict, Optional

from src.domain.interfaces.exchange_api_interface import (
    ExchangeApiInterface,
    OrderRequest as ExchangeOrderRequest,
    OrderResult
)
from src.infrastructure.services.service_container import ServiceContainer
from src.interactor.dtos.send_market_order_dtos import (
    SendMarketOrderInputDto,
    SendMarketOrderOutputDto,
)
from src.interactor.errors.error_classes import (
    LoginFailedException,
    ItemNotCreatedException,
    SendMarketOrderFailedException,
)
from src.interactor.interfaces.logger.logger import LoggerInterface
from src.interactor.interfaces.presenters.send_market_order_presenter import (
    SendMarketOrderPresenterInterface,
)
from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface
from src.interactor.validations.send_market_order_validator import SendMarketOrderInputDtoValidator


class SendMarketOrderUseCaseV2:
    """Handles sending market orders using abstracted exchange API.
    
    This version uses the new ExchangeApiInterface instead of direct PFCF calls,
    making it broker-agnostic.
    """
    
    def __init__(
        self,
        presenter: SendMarketOrderPresenterInterface,
        service_container: ServiceContainer,
        logger: LoggerInterface,
        session_repository: SessionRepositoryInterface,
        exchange_api: Optional[ExchangeApiInterface] = None,
    ) -> None:
        """Initialize the send market order use case.
        
        Args:
            presenter: Presenter for formatting output.
            service_container: Container with all application services.
            logger: Logger for application logging.
            session_repository: Repository for session management.
            exchange_api: Optional exchange API, defaults to v2 from container.
        """
        self.presenter = presenter
        self.service_container = service_container
        self.logger = logger
        self.session_repository = session_repository
        self.exchange_api = exchange_api or service_container.exchange_api_v2
        
        if not self.exchange_api:
            raise ValueError("Exchange API v2 not available in service container")
    
    def execute(self, input_dto: SendMarketOrderInputDto) -> SendMarketOrderOutputDto:
        """Execute the market order using abstracted API.
        
        Args:
            input_dto: Input data for the market order.
            
        Returns:
            SendMarketOrderOutputDto with order execution result.
            
        Raises:
            LoginFailedException: If user is not logged in.
            SendMarketOrderFailedException: If order fails.
        """
        try:
            # Validate input
            validator = SendMarketOrderInputDtoValidator(input_dto)
            if not validator.validate():
                raise ItemNotCreatedException({"error": validator.errors})
            
            # Check if user is logged in
            user_id = self.service_container.user_id if hasattr(self.service_container, 'user_id') else None
            if not user_id:
                # Try to get from session
                sessions = self.session_repository.get_all()
                if sessions:
                    user_id = sessions[0].user_id
                    
            if not user_id:
                raise LoginFailedException()
            
            # Check if exchange is connected
            if not self.exchange_api.is_connected():
                raise SendMarketOrderFailedException("Exchange not connected")
            
            # Convert DTO to exchange order request
            order_request = self._convert_to_order_request(input_dto)
            
            # Send order using abstract API
            self.logger.log_info(
                f"Sending market order: {order_request.symbol} "
                f"{order_request.side} {order_request.quantity}"
            )
            
            order_result = self.exchange_api.send_order(order_request)
            
            # Convert result to output DTO
            output_dto = self._convert_from_order_result(order_result, input_dto)
            
            # Present result
            self.presenter.present(output_dto)
            
            return output_dto
            
        except LoginFailedException:
            self.logger.log_error("User not logged in for market order")
            raise
        except Exception as e:
            self.logger.log_error(f"Market order failed: {str(e)}")
            raise SendMarketOrderFailedException(str(e))
    
    def _convert_to_order_request(self, input_dto: SendMarketOrderInputDto) -> ExchangeOrderRequest:
        """Convert internal DTO to exchange order request.
        
        Args:
            input_dto: Internal order DTO.
            
        Returns:
            Standard exchange order request.
        """
        return ExchangeOrderRequest(
            account=input_dto.order_account,
            symbol=input_dto.item_code,
            side='BUY' if input_dto.side.value == 'BUY' else 'SELL',
            order_type='MARKET',  # Always market order for this use case
            quantity=input_dto.quantity,
            price=input_dto.price,
            time_in_force=input_dto.time_in_force.value,
            note=input_dto.note
        )
    
    def _convert_from_order_result(
        self, 
        order_result: OrderResult, 
        input_dto: SendMarketOrderInputDto
    ) -> SendMarketOrderOutputDto:
        """Convert exchange result to output DTO.
        
        Args:
            order_result: Result from exchange.
            input_dto: Original input for reference.
            
        Returns:
            Output DTO with order result.
        """
        return SendMarketOrderOutputDto(
            is_send_order=order_result.success,
            note=order_result.message or input_dto.note,
            order_serial=order_result.order_id or "",
            error_code=order_result.error_code or "",
            error_message=order_result.message or ""
        )