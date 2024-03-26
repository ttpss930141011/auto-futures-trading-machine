from abc import ABC, abstractmethod


class PFCFClientInterface(ABC):
    @abstractmethod
    def get_client(self):
        pass

    # Add other methods and attributes as needed
