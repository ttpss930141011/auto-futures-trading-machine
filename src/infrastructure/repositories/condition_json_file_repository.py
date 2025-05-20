from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict, Optional, List

from src.domain.entities.condition import Condition
from src.domain.value_objects import OrderOperation
from src.interactor.interfaces.repositories.condition_repository import (
    ConditionRepositoryInterface,
)


class ConditionJsonFileRepository(ConditionRepositoryInterface):
    """Condition repository that persists data to a JSON file.

    This implementation allows multiple processes to share trading conditions
    by reading from and writing to a single JSON file on disk.
    """

    # Use pathlib for safer, clearer path construction
    DEFAULT_FILENAME: str = str(
        Path(__file__).resolve().parent.parent.parent / "data" / "conditions.json"
    )

    def __init__(self, file_path: str | None = None) -> None:
        """Create a new repository instance.

        Args:
            file_path: Optional custom path for the JSON file. If *None*, the
                repository will use the :pyattr:`DEFAULT_FILENAME`.
        """
        self._file_path: str = file_path or self.DEFAULT_FILENAME

        # Ensure parent directory exists.
        Path(self._file_path).parent.mkdir(parents=True, exist_ok=True)

        # Load existing data if available, otherwise initialize empty store.
        self._data: Dict[uuid.UUID, Condition] = {}
        self._load()

    # ---------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------
    def _load(self) -> None:
        """Load data from the JSON file into memory."""
        if not Path(self._file_path).is_file():
            # Nothing to load; keep empty store.
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as fp:
                raw_data: List[dict] = json.load(fp)

            converted: Dict[uuid.UUID, Condition] = {}
            for item in raw_data:
                try:
                    item["condition_id"] = uuid.UUID(item["condition_id"])
                    if isinstance(item["action"], str):
                        item["action"] = OrderOperation[item["action"]]
                    converted[item["condition_id"]] = Condition.from_dict(item)
                except (KeyError, ValueError):
                    # Skip invalid records but continue loading others.
                    continue

            self._data = converted
        except (json.JSONDecodeError, OSError, KeyError, ValueError):
            # If loading fails, fallback to empty store. In production you may
            # want to log the error or re-raise.
            self._data = {}

    def _save(self) -> None:
        """Persist in-memory data to the JSON file on disk."""
        serialisable: List[dict] = []
        for cond in self._data.values():
            item = cond.to_dict()
            # Ensure UUIDs and Enums are serialisable
            item["condition_id"] = str(item["condition_id"])
            if isinstance(item["action"], OrderOperation):
                item["action"] = item["action"].name
            serialisable.append(item)
        with open(self._file_path, "w", encoding="utf-8") as fp:
            json.dump(serialisable, fp, ensure_ascii=False, indent=2)

    # ---------------------------------------------------------------------
    # Repository interface implementation
    # ---------------------------------------------------------------------
    def get(self, condition_id: uuid.UUID) -> Optional[Condition]:
        return self._data.get(condition_id)

    def get_all(self) -> Dict[uuid.UUID, Condition]:
        return self._data

    def search_by_trigger_price(self, trigger_price: int) -> Dict[uuid.UUID, Condition]:
        return {
            cid: cond for cid, cond in self._data.items() if cond.trigger_price == trigger_price
        }

    def create(
        self,
        action: OrderOperation,
        trigger_price: int,
        turning_point: int,
        quantity: int,
        take_profit_point: int,
        stop_loss_point: int,
        is_following: bool,
    ) -> Condition:
        condition_id = uuid.uuid4()
        condition = Condition(
            condition_id=condition_id,
            action=action,
            trigger_price=trigger_price,
            quantity=quantity,
            turning_point=turning_point,
            take_profit_point=take_profit_point,
            stop_loss_point=stop_loss_point,
            is_following=is_following,
        )
        self._data[condition.condition_id] = condition
        self._save()
        return condition

    def delete(self, condition_id: uuid.UUID) -> bool:
        if condition_id in self._data:
            del self._data[condition_id]
            self._save()
            return True
        return False

    def delete_all(self) -> bool:
        self._data = {}
        self._save()
        return True

    def update(self, condition: Condition) -> Condition:
        self._data[condition.condition_id] = condition
        self._save()
        return condition
