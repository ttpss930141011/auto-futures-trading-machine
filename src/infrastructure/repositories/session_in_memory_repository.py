import time

from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


class SessionInMemoryRepository(SessionRepositoryInterface):
    _instance = None

    def __new__(cls, session_timeout=3):
        if not cls._instance:
            cls._instance = super(SessionInMemoryRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, session_timeout=3):
        self._session_data = {}
        self.session_timeout = session_timeout  # session timeout in seconds

    def create_session(self, account: str):
        self._session_data['account'] = account
        self._session_data['logged_in'] = True
        self._session_data['expiration_time'] = time.time() + self.session_timeout
        self._session_data['order_account'] = None
        self._session_data['order_account_set'] = None

    def get_current_user(self):
        if self._session_expired():
            self.destroy_session()
            return None
        return self._session_data.get('account')

    def is_user_logged_in(self):
        if self._session_expired():
            self.destroy_session()
            return False
        return self._session_data.get('logged_in', False)

    def destroy_session(self):
        self._session_data = {}

    def _session_expired(self):
        return time.time() > self._session_data.get('expiration_time', 0)

    def renew_session(self):
        if self.is_user_logged_in():
            self._session_data['expiration_time'] = time.time() + self.session_timeout

    def set_order_account(self, account):
        self._session_data['order_account'] = account

    def get_order_account(self):
        return self._session_data.get('order_account')

    def set_order_account_set(self, account_set):
        self._session_data['order_account_set'] = account_set

    def set_item_code(self, item_code):
        self._session_data['item_code'] = item_code

    def get_item_code(self):
        return self._session_data.get('item_code')
