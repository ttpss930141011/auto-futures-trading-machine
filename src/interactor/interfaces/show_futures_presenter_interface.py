from abc import ABC, abstractmethod
from src.interactor.dtos.show_futures_dtos import ShowFuturesOutputDto


class ShowFuturesPresenterInterface(ABC):
    """ Interface for futures presenter
    """

    @abstractmethod
    def present_futures_data(self, futures_data) -> ShowFuturesOutputDto:
        """ Present futures data
        """
        pass

    @abstractmethod
    def present_error(self, error_message: str) -> ShowFuturesOutputDto:
        """ Present error message
        """
        pass 