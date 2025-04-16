from src.interactor.dtos.show_futures_dtos import FutureDataDto, ShowFuturesOutputDto
from src.interactor.interfaces.presenters.show_futures_presenter import ShowFuturesPresenterInterface


class ShowFuturesPresenter(ShowFuturesPresenterInterface):
    """ Presenter for displaying futures data
    """

    def present_futures_data(self, futures_data) -> ShowFuturesOutputDto:
        """ Format futures data into DTOs
        """
        if not futures_data:
            return ShowFuturesOutputDto(success=False, message="No futures data found")

        futures_dtos = []
        for data in futures_data:
            try:
                future_dto = FutureDataDto(
                    commodity_id=str(data.COMMODITYID),
                    product_name=str(data.desc),
                    underlying_id="",  # Not available in this data structure
                    delivery_month=str(data.month),
                    market_code=str(data.Class),
                    position_price=str(data.Premium),
                    expiration_date="",  # Not available in this data structure
                    max_price=float(data.MaxPrice) if data.MaxPrice else 0.0,
                    min_price=float(data.MinPrice) if data.MinPrice else 0.0
                )
                futures_dtos.append(future_dto)
            except (AttributeError, ValueError) as e:
                # If there's an error converting the data, skip this item
                continue

        if not futures_dtos:
            return ShowFuturesOutputDto(success=False, message="No valid futures data found")

        return ShowFuturesOutputDto(
            success=True,
            message=f"Found {len(futures_dtos)} futures items",
            futures_data=futures_dtos
        )

    def present_error(self, error_message: str) -> ShowFuturesOutputDto:
        """ Present error message
        """
        return ShowFuturesOutputDto(
            success=False,
            message=f"Error: {error_message}"
        ) 