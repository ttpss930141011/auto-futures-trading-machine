"""Tests for Base Input Validator."""

import pytest
from src.interactor.validations.base_input_validator import BaseInputValidator


class TestBaseInputValidator:
    """Test cases for BaseInputValidator."""

    def test_initialization(self):
        """Test validator initialization."""
        data = {"field1": "value1", "field2": "value2"}
        validator = BaseInputValidator(data)
        
        assert validator.data == data
        assert validator.errors == {}

    def test_required_field_validation_success(self):
        """Test required field validation when field is present."""
        data = {"username": "testuser"}
        schema = {"username": {"required": True}}
        
        validator = BaseInputValidator(data)
        validator.verify(schema)
        
        assert validator.errors == {}

    def test_required_field_validation_failure(self):
        """Test required field validation when field is missing."""
        data = {}
        schema = {"username": {"required": True}}
        
        validator = BaseInputValidator(data)
        
        with pytest.raises(ValueError, match="Username: required field"):
            validator.verify(schema)

    def test_null_value_validation(self):
        """Test null value validation."""
        data = {"username": None}
        schema = {"username": {"required": True}}
        
        validator = BaseInputValidator(data)
        
        with pytest.raises(ValueError, match="Username: null value not allowed"):
            validator.verify(schema)

    def test_multiple_field_validation(self):
        """Test validation with multiple fields."""
        data = {"username": "testuser", "email": "test@example.com"}
        schema = {
            "username": {"required": True},
            "email": {"required": True},
            "age": {"required": False}
        }
        
        validator = BaseInputValidator(data)
        validator.verify(schema)
        
        assert validator.errors == {}

    def test_error_reset_on_verify(self):
        """Test that errors are reset on each verify call."""
        schema1 = {"field1": {"required": True}}
        
        validator = BaseInputValidator({})
        
        # First verify should raise error
        with pytest.raises(ValueError):
            validator.verify(schema1)
        
        # Update data and verify again - should pass
        validator.data = {"field1": "value"}
        validator.verify(schema1)  # Should not raise exception
        assert validator.errors == {}
