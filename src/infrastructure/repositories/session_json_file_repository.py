from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional, Any, Dict

from src.interactor.interfaces.repositories.session_repository import SessionRepositoryInterface


class SessionJsonFileRepository(SessionRepositoryInterface):
    """
    File-based session repository storing session state in a JSON file.

    This implementation allows multiple processes to share session data
    by reading from and writing to a single JSON file on disk.
    """

    DEFAULT_FILENAME: str = str(
        Path(__file__).resolve().parent.parent.parent.parent / "tmp" / "session.json"
    )

    def __init__(self, session_timeout: int) -> None:
        """
        Initialize the JSON file session repository.

        Args:
            session_timeout: Session timeout in seconds.
        """
        self.session_timeout = session_timeout
        self.file_path = Path(self.DEFAULT_FILENAME)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write({})

    def _read_data(self) -> Dict[str, Any]:
        """Read session data from the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _write(self, data: Dict[str, Any]) -> None:
        """Write session data to the JSON file."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _is_expired(self, expiration_time: float) -> bool:
        """Check if the session has expired based on expiration_time."""
        return time.time() > expiration_time

    def create_session(self, account: str) -> None:
        """
        Create a new user session.

        Args:
            account: The user account identifier.
        """
        data: Dict[str, Any] = {
            "account": account,
            "logged_in": True,
            "expiration_time": time.time() + self.session_timeout,
            "order_account": None,
            "item_code": None,
        }
        self._write(data)

    def get_current_user(self) -> Optional[str]:
        """
        Get the current logged in user if session is valid.

        Returns:
            The account identifier or None if no valid session.
        """
        data = self._read_data()
        expiration_time = data.get("expiration_time", 0)
        if not data.get("logged_in") or self._is_expired(expiration_time):
            self.destroy_session()
            return None
        return data.get("account")

    def is_user_logged_in(self) -> bool:
        """
        Check if a user is logged in and session is valid.

        Returns:
            True if logged in and session not expired, False otherwise.
        """
        data = self._read_data()
        expiration_time = data.get("expiration_time", 0)
        if not data.get("logged_in") or self._is_expired(expiration_time):
            self.destroy_session()
            return False
        return True

    def destroy_session(self) -> None:
        """Destroy the current session."""
        self._write({})

    def renew_session(self) -> None:
        """
        Renew the session expiration time if user is logged in.

        Does nothing if no valid session.
        """
        data = self._read_data()
        if data.get("logged_in"):
            data["expiration_time"] = time.time() + self.session_timeout
            self._write(data)

    def set_order_account(self, account: str) -> None:
        """
        Set the order account for the session.

        Args:
            account: The order account identifier.
        """
        data = self._read_data()
        data["order_account"] = account
        self._write(data)

    def get_order_account(self) -> Optional[str]:
        """
        Get the order account from the session.

        Returns:
            The order account identifier or None if not set.
        """
        data = self._read_data()
        return data.get("order_account")

    def set_order_account_set(self, account_set: Any) -> None:
        """
        Set the available order account set for the session.

        Args:
            account_set: The account set.
        """
        data = self._read_data()
        # Convert .NET System.String[] (or other iterable) to Python list for JSON serialization
        try:
            account_list = [str(item) for item in account_set]
        except Exception:
            account_list = account_set
        data["order_account_set"] = account_list
        self._write(data)

    def set_item_code(self, item_code: str) -> None:
        """
        Set the item code for the session.

        Args:
            item_code: The item code identifier.
        """
        data = self._read_data()
        data["item_code"] = item_code
        self._write(data)

    def get_item_code(self) -> Optional[str]:
        """
        Get the item code from the session.

        Returns:
            The item code identifier or None if not set.
        """
        data = self._read_data()
        return data.get("item_code")

    def set_auth_details(self, password: str, ip_address: str) -> None:
        """
        TEMPORARY: Store authentication details for order executor process.
        WARNING: This is insecure and should only be used for development.
        In production, use a secure credential store or token-based auth.

        Args:
            password: The user password (will be stored temporarily)
            ip_address: The exchange server address
        """
        data = self._read_data()
        # Add a warning marker to indicate this is temporary
        data["_temp_auth"] = {
            "password": password,
            "ip_address": ip_address,
            "warning": "TEMPORARY - DO NOT USE IN PRODUCTION",
        }
        self._write(data)

    def get_auth_details(self) -> Optional[Dict[str, str]]:
        """
        TEMPORARY: Retrieve authentication details.
        WARNING: This is insecure and should only be used for development.

        Returns:
            Dict with password and ip_address, or None if not available
        """
        data = self._read_data()
        return data.get("_temp_auth")

    def clear_auth_details(self) -> None:
        """
        Clear temporary authentication details.
        """
        data = self._read_data()
        if "_temp_auth" in data:
            del data["_temp_auth"]
            self._write(data)
