"""Tests for domain value objects."""

import pytest
import uuid

from src.domain.value_objects import (
    OrderOperation,
    OrderTypeEnum,
    TimeInForce,
    OpenClose,
    DayTrade,
    ConditionId,
)


class TestOrderOperation:
    """Test cases for OrderOperation enum."""

    def test_order_operation_values(self):
        """Test OrderOperation enum values."""
        assert OrderOperation.BUY.value == "buy"
        assert OrderOperation.SELL.value == "sell"

    def test_order_operation_string_representation(self):
        """Test OrderOperation string representation."""
        assert str(OrderOperation.BUY) == "buy"
        assert str(OrderOperation.SELL) == "sell"

    def test_order_operation_equality(self):
        """Test OrderOperation equality."""
        assert OrderOperation.BUY == OrderOperation.BUY
        assert OrderOperation.SELL == OrderOperation.SELL
        assert OrderOperation.BUY != OrderOperation.SELL

    def test_order_operation_unique_values(self):
        """Test that all OrderOperation values are unique."""
        values = [op.value for op in OrderOperation]
        assert len(values) == len(set(values))


class TestOrderTypeEnum:
    """Test cases for OrderTypeEnum."""

    def test_order_type_values(self):
        """Test OrderTypeEnum values."""
        assert OrderTypeEnum.Limit.value == "Limit"
        assert OrderTypeEnum.Market.value == "Market"
        assert OrderTypeEnum.MarketPrice.value == "MarketPrice"

    def test_order_type_string_representation(self):
        """Test OrderTypeEnum string representation."""
        assert str(OrderTypeEnum.Limit) == "Limit"
        assert str(OrderTypeEnum.Market) == "Market"
        assert str(OrderTypeEnum.MarketPrice) == "MarketPrice"

    def test_order_type_equality(self):
        """Test OrderTypeEnum equality."""
        assert OrderTypeEnum.Limit == OrderTypeEnum.Limit
        assert OrderTypeEnum.Market == OrderTypeEnum.Market
        assert OrderTypeEnum.Limit != OrderTypeEnum.Market

    def test_order_type_unique_values(self):
        """Test that all OrderTypeEnum values are unique."""
        values = [ot.value for ot in OrderTypeEnum]
        assert len(values) == len(set(values))


class TestTimeInForce:
    """Test cases for TimeInForce enum."""

    def test_time_in_force_values(self):
        """Test TimeInForce enum values."""
        assert TimeInForce.ROD.value == "ROD"
        assert TimeInForce.IOC.value == "IOC"
        assert TimeInForce.FOK.value == "FOK"

    def test_time_in_force_string_representation(self):
        """Test TimeInForce string representation."""
        assert str(TimeInForce.ROD) == "ROD"
        assert str(TimeInForce.IOC) == "IOC"
        assert str(TimeInForce.FOK) == "FOK"

    def test_time_in_force_equality(self):
        """Test TimeInForce equality."""
        assert TimeInForce.ROD == TimeInForce.ROD
        assert TimeInForce.IOC == TimeInForce.IOC
        assert TimeInForce.ROD != TimeInForce.IOC

    def test_time_in_force_unique_values(self):
        """Test that all TimeInForce values are unique."""
        values = [tif.value for tif in TimeInForce]
        assert len(values) == len(set(values))


class TestOpenClose:
    """Test cases for OpenClose enum."""

    def test_open_close_values(self):
        """Test OpenClose enum values."""
        assert OpenClose.OPEN.value == "Y"
        assert OpenClose.CLOSE.value == "N"
        assert OpenClose.AUTO.value == "AUTO"

    def test_open_close_string_representation(self):
        """Test OpenClose string representation."""
        assert str(OpenClose.OPEN) == "Y"
        assert str(OpenClose.CLOSE) == "N"
        assert str(OpenClose.AUTO) == "AUTO"

    def test_open_close_equality(self):
        """Test OpenClose equality."""
        assert OpenClose.OPEN == OpenClose.OPEN
        assert OpenClose.CLOSE == OpenClose.CLOSE
        assert OpenClose.OPEN != OpenClose.CLOSE

    def test_open_close_unique_values(self):
        """Test that all OpenClose values are unique."""
        values = [oc.value for oc in OpenClose]
        assert len(values) == len(set(values))


class TestDayTrade:
    """Test cases for DayTrade enum."""

    def test_day_trade_values(self):
        """Test DayTrade enum values."""
        assert DayTrade.Yes.value == "Y"
        assert DayTrade.No.value == "N"

    def test_day_trade_string_representation(self):
        """Test DayTrade string representation."""
        assert str(DayTrade.Yes) == "Y"
        assert str(DayTrade.No) == "N"

    def test_day_trade_equality(self):
        """Test DayTrade equality."""
        assert DayTrade.Yes == DayTrade.Yes
        assert DayTrade.No == DayTrade.No
        assert DayTrade.Yes != DayTrade.No

    def test_day_trade_unique_values(self):
        """Test that all DayTrade values are unique."""
        values = [dt.value for dt in DayTrade]
        assert len(values) == len(set(values))


class TestConditionId:
    """Test cases for ConditionId (UUID alias)."""

    def test_condition_id_is_uuid_type(self):
        """Test that ConditionId is a UUID type."""
        assert ConditionId == uuid.UUID

    def test_condition_id_creation(self):
        """Test ConditionId creation from string."""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        condition_id = ConditionId(uuid_str)
        
        assert isinstance(condition_id, uuid.UUID)
        assert str(condition_id) == uuid_str

    def test_condition_id_random_generation(self):
        """Test ConditionId can be generated randomly."""
        condition_id1 = uuid.uuid4()
        condition_id2 = uuid.uuid4()
        
        assert isinstance(condition_id1, ConditionId)
        assert isinstance(condition_id2, ConditionId)
        assert condition_id1 != condition_id2

    def test_condition_id_equality(self):
        """Test ConditionId equality."""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        condition_id1 = ConditionId(uuid_str)
        condition_id2 = ConditionId(uuid_str)
        condition_id3 = uuid.uuid4()
        
        assert condition_id1 == condition_id2
        assert condition_id1 != condition_id3