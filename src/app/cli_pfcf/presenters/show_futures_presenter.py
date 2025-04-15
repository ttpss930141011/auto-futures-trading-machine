from src.interactor.dtos.show_futures_dtos import FutureDataDto, ShowFuturesOutputDto
from src.interactor.interfaces.show_futures_presenter_interface import ShowFuturesPresenterInterface


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
            future_dto = FutureDataDto(
                commodity_id=data.COMMODITYID,
                product_name=data.PRODUCTNAME,
                underlying_id=data.UNDERLYINGID,
                delivery_month=data.DELIVERYMONTH,
                market_code=data.MARKETCODE,
                position_price=data.POSITIONPRICE,
                expiration_date=data.EXPIRATIONDATE
            )
            futures_dtos.append(future_dto)

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