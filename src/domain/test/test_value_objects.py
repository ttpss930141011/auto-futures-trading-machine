"""Tests for domain value objects."""

import pytest
from datetime import datetime
from decimal import Decimal

from src.domain.value_objects import (
    Price,
    Quantity,
    OrderId,
    ItemCode,
)


class TestPrice:
    """Test cases for Price value object."""

    def test_price_creation_with_decimal(self):
        """Test Price can be created with Decimal value."""
        price_value = Decimal("100.50")
        price = Price(price_value)
        
        assert price.value == price_value
        assert isinstance(price.value, Decimal)

    def test_price_creation_with_float(self):
        """Test Price can be created with float value."""
        price_value = 100.50
        price = Price(price_value)
        
        assert price.value == Decimal("100.50")
        assert isinstance(price.value, Decimal)

    def test_price_creation_with_int(self):
        """Test Price can be created with int value."""
        price_value = 100
        price = Price(price_value)
        
        assert price.value == Decimal("100")
        assert isinstance(price.value, Decimal)

    def test_price_creation_with_string(self):
        """Test Price can be created with string value."""
        price_value = "100.50"
        price = Price(price_value)
        
        assert price.value == Decimal("100.50")
        assert isinstance(price.value, Decimal)

    def test_price_equality(self):
        """Test Price equality comparison."""
        price1 = Price(Decimal("100.50"))
        price2 = Price(Decimal("100.50"))
        price3 = Price(Decimal("200.00"))
        
        assert price1 == price2
        assert price1 != price3

    def test_price_str_representation(self):
        """Test Price string representation."""
        price = Price(Decimal("100.50"))
        assert str(price) == "100.50"

    def test_price_repr_representation(self):
        """Test Price repr representation."""
        price = Price(Decimal("100.50"))
        assert repr(price) == "Price(100.50)"

    def test_price_validation_negative_value(self):
        """Test Price raises error for negative values."""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            Price(Decimal("-10.00"))

    def test_price_validation_zero_value(self):
        """Test Price allows zero value."""
        price = Price(Decimal("0.00"))
        assert price.value == Decimal("0.00")


class TestQuantity:
    """Test cases for Quantity value object."""

    def test_quantity_creation_with_int(self):
        """Test Quantity can be created with int value."""
        quantity = Quantity(10)
        
        assert quantity.value == 10
        assert isinstance(quantity.value, int)

    def test_quantity_creation_with_string(self):
        """Test Quantity can be created with string value."""
        quantity = Quantity("10")
        
        assert quantity.value == 10
        assert isinstance(quantity.value, int)

    def test_quantity_equality(self):
        """Test Quantity equality comparison."""
        quantity1 = Quantity(10)
        quantity2 = Quantity(10)
        quantity3 = Quantity(20)
        
        assert quantity1 == quantity2
        assert quantity1 != quantity3

    def test_quantity_str_representation(self):
        """Test Quantity string representation."""
        quantity = Quantity(10)
        assert str(quantity) == "10"

    def test_quantity_repr_representation(self):
        """Test Quantity repr representation."""
        quantity = Quantity(10)
        assert repr(quantity) == "Quantity(10)"

    def test_quantity_validation_negative_value(self):
        """Test Quantity raises error for negative values."""
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            Quantity(-10)

    def test_quantity_validation_zero_value(self):
        """Test Quantity allows zero value."""
        quantity = Quantity(0)
        assert quantity.value == 0


class TestOrderId:
    """Test cases for OrderId value object."""

    def test_order_id_creation(self):
        """Test OrderId can be created with string value."""
        order_id = OrderId("ORD123")
        
        assert order_id.value == "ORD123"
        assert isinstance(order_id.value, str)

    def test_order_id_equality(self):
        """Test OrderId equality comparison."""
        order_id1 = OrderId("ORD123")
        order_id2 = OrderId("ORD123")
        order_id3 = OrderId("ORD456")
        
        assert order_id1 == order_id2
        assert order_id1 != order_id3

    def test_order_id_str_representation(self):
        """Test OrderId string representation."""
        order_id = OrderId("ORD123")
        assert str(order_id) == "ORD123"

    def test_order_id_repr_representation(self):
        """Test OrderId repr representation."""
        order_id = OrderId("ORD123")
        assert repr(order_id) == "OrderId(ORD123)"

    def test_order_id_validation_empty_value(self):
        """Test OrderId raises error for empty values."""
        with pytest.raises(ValueError, match="OrderId cannot be empty"):
            OrderId("")

    def test_order_id_validation_none_value(self):
        """Test OrderId raises error for None values."""
        with pytest.raises(ValueError, match="OrderId cannot be empty"):
            OrderId(None)


class TestItemCode:
    """Test cases for ItemCode value object."""

    def test_item_code_creation(self):
        """Test ItemCode can be created with string value."""
        item_code = ItemCode("MXFL2")
        
        assert item_code.value == "MXFL2"
        assert isinstance(item_code.value, str)

    def test_item_code_equality(self):
        """Test ItemCode equality comparison."""
        item_code1 = ItemCode("MXFL2")
        item_code2 = ItemCode("MXFL2")
        item_code3 = ItemCode("TXFL2")
        
        assert item_code1 == item_code2
        assert item_code1 != item_code3

    def test_item_code_str_representation(self):
        """Test ItemCode string representation."""
        item_code = ItemCode("MXFL2")
        assert str(item_code) == "MXFL2"

    def test_item_code_repr_representation(self):
        """Test ItemCode repr representation."""
        item_code = ItemCode("MXFL2")
        assert repr(item_code) == "ItemCode(MXFL2)"

    def test_item_code_validation_empty_value(self):
        """Test ItemCode raises error for empty values."""
        with pytest.raises(ValueError, match="ItemCode cannot be empty"):
            ItemCode("")

    def test_item_code_validation_none_value(self):
        """Test ItemCode raises error for None values."""
        with pytest.raises(ValueError, match="ItemCode cannot be empty"):
            ItemCode(None)

    def test_item_code_case_sensitivity(self):
        """Test ItemCode is case sensitive."""
        item_code1 = ItemCode("mxfl2")
        item_code2 = ItemCode("MXFL2")
        
        assert item_code1 != item_code2