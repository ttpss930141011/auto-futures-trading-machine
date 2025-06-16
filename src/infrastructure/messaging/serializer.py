"""Msgpack Serialization Utilities."""

import msgpack
from typing import Any, Dict, Type, TypeVar
import datetime
import enum

from src.infrastructure.events.tick import Tick, TickEvent
from src.infrastructure.events.trading_signal import TradingSignal
from src.domain.value_objects import OrderOperation

# Define a type variable for specific serializable types
T = TypeVar("T", Tick, TickEvent, TradingSignal, OrderOperation)


# --- Encoding/Serialization Helpers ---


def _encode_datetime(obj: Any) -> Any:
    """Custom encoder for datetime objects."""
    if isinstance(obj, datetime.datetime):
        # Convert to POSIX timestamp (float) with microsecond precision
        return {"__datetime__": True, "timestamp": obj.timestamp()}
    return obj


def _encode_enum(obj: Any) -> Any:
    """Custom encoder for Enum objects."""
    if isinstance(obj, enum.Enum):
        return {"__enum__": True, "class": obj.__class__.__name__, "name": obj.name}
    return obj


def _default_encoder(obj: Any) -> Any:
    """Chain custom encoders."""
    obj = _encode_datetime(obj)
    obj = _encode_enum(obj)
    # Add more custom encoders here if needed

    # If it's one of our known types, convert to dict
    if isinstance(obj, (Tick, TickEvent, TradingSignal)):
        # Add class name for reconstruction
        data = obj.__dict__.copy()
        data["__class__"] = obj.__class__.__name__
        return data

    # Let msgpack handle built-in types or raise TypeError for unsupported types
    return obj


# --- Decoding/Deserialization Helpers ---

# Map class names back to actual classes for reconstruction
CLASS_REGISTRY: Dict[str, Type[T]] = {
    "Tick": Tick,
    "TickEvent": TickEvent,
    "TradingSignal": TradingSignal,
    "OrderOperation": OrderOperation,
}


def _decode_datetime(dct: Dict[str, Any]) -> Any:
    """Custom object hook for decoding datetime objects."""
    if "__datetime__" in dct:
        # Convert timestamp back to datetime object (UTC assumed if no timezone info)
        # Using fromtimestamp handles potential float precision issues better
        return datetime.datetime.fromtimestamp(dct["timestamp"], datetime.timezone.utc)
    return dct


def _decode_enum(dct: Dict[str, Any]) -> Any:
    """Custom object hook for decoding Enum objects."""
    if "__enum__" in dct:
        enum_class_name = dct["class"]
        member_name = dct["name"]
        enum_class = CLASS_REGISTRY.get(enum_class_name)
        if enum_class and issubclass(enum_class, enum.Enum):
            try:
                return enum_class[member_name]
            except KeyError as exc:
                # Handle cases where enum member might not exist (e.g., version mismatch)
                raise ValueError(
                    f"Unknown enum member '{member_name}' for class '{enum_class_name}'"
                ) from exc
        else:
            raise TypeError(f"Cannot find or reconstruct enum class '{enum_class_name}'")
    return dct


def _object_hook(dct: Dict[str, Any]) -> Any:
    """Chain custom decoders and handle class reconstruction.

    This function is called by ``msgpack.unpackb`` for every *dict* encountered in
    the packed payload.  However, some earlier decoders (e.g. ``_decode_datetime``)
    may convert the mapping into a *non-dict* object (such as ``datetime`` or an
    ``Enum`` instance).  Subsequent processing steps must therefore ignore those
    non-mapping objects to avoid ``TypeError: argument of type 'X' is not iterable``
    errors when using the ``in`` operator.  The guard at the top of this function
    ensures that once the data ceases to be a mapping, it is immediately returned
    without further processing.
    """

    # First apply the custom decoders. They might convert *dct* into a non-dict
    # object (e.g., ``datetime``), so we must stop the pipeline early in that
    # case.
    dct = _decode_datetime(dct)

    # If the object is no longer a ``dict`` we cannot (and should not) continue
    # treating it as such, so return it directly.
    if not isinstance(dct, dict):
        return dct

    dct = _decode_enum(dct)

    # Again ensure *dct* is still a ``dict`` before proceeding.
    if not isinstance(dct, dict):
        return dct

    # Add more custom decoders here before class reconstruction

    if "__class__" in dct:
        class_name = dct.pop("__class__")
        cls = CLASS_REGISTRY.get(class_name)
        if cls:
            # Reconstruct the object using its __init__
            try:
                # Assumes __init__ args match keys in dct
                return cls(**dct)
            except TypeError as e:
                # Handle cases where __init__ signature doesn't match dictionary keys
                raise TypeError(f"Failed to reconstruct {class_name}: {e}. Data: {dct}") from e
        else:
            # Handle unknown classes if necessary, or raise an error
            raise TypeError(f"Cannot reconstruct unknown class '{class_name}'")

    return dct


# --- Public API ---


def serialize(data: Any) -> bytes:
    """Serialize Python object to msgpack bytes using custom encoders."""
    return msgpack.packb(data, default=_default_encoder, use_bin_type=True)


def deserialize(payload: bytes) -> Any:
    """Deserialize msgpack bytes to Python object using custom decoders."""
    # Set raw=False to decode strings as utf-8 by default
    return msgpack.unpackb(payload, object_hook=_object_hook, raw=False)
