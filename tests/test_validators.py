"""Tests for validation utilities."""

import pytest
import numpy as np
from src.utils.validators import (
    validate_motor_id,
    validate_angle,
    validate_coordinate,
    validate_leg_id,
    validate_momentum,
    validate_positive_number
)
from src.utils.exceptions import ValidationError


class TestMotorIdValidation:
    """Test motor ID validation."""

    def test_valid_motor_id(self):
        """Test valid motor IDs."""
        for motor_id in range(10):
            validate_motor_id(motor_id)  # Should not raise

    def test_invalid_motor_id_negative(self):
        """Test negative motor ID."""
        with pytest.raises(ValidationError, match="Invalid motor_id"):
            validate_motor_id(-1)

    def test_invalid_motor_id_too_large(self):
        """Test motor ID too large."""
        with pytest.raises(ValidationError, match="Invalid motor_id"):
            validate_motor_id(10)

    def test_invalid_motor_id_type(self):
        """Test non-integer motor ID."""
        with pytest.raises(ValidationError, match="Invalid motor_id"):
            validate_motor_id("0")


class TestAngleValidation:
    """Test angle validation."""

    def test_valid_angle(self):
        """Test valid angles."""
        validate_angle(0)
        validate_angle(90)
        validate_angle(180)
        validate_angle(45.5)

    def test_invalid_angle_too_small(self):
        """Test angle too small."""
        with pytest.raises(ValidationError, match="out of range"):
            validate_angle(-1)

    def test_invalid_angle_too_large(self):
        """Test angle too large."""
        with pytest.raises(ValidationError, match="out of range"):
            validate_angle(181)

    def test_custom_range(self):
        """Test custom angle range."""
        validate_angle(50, min_angle=0, max_angle=100)
        with pytest.raises(ValidationError):
            validate_angle(150, min_angle=0, max_angle=100)


class TestCoordinateValidation:
    """Test coordinate validation."""

    def test_valid_coordinate(self):
        """Test valid coordinates."""
        validate_coordinate(0)
        validate_coordinate(10.5)
        validate_coordinate(-5)

    def test_invalid_coordinate_type(self):
        """Test non-numeric coordinate."""
        with pytest.raises(ValidationError, match="Invalid"):
            validate_coordinate("10")


class TestLegIdValidation:
    """Test leg ID validation."""

    def test_valid_leg_id(self):
        """Test valid leg IDs."""
        for leg_id in ('FL', 'FR', 'BL', 'BR'):
            validate_leg_id(leg_id)

    def test_invalid_leg_id(self):
        """Test invalid leg ID."""
        with pytest.raises(ValidationError, match="Invalid leg_id"):
            validate_leg_id('XX')

    def test_invalid_leg_id_type(self):
        """Test non-string leg ID."""
        with pytest.raises(ValidationError, match="Invalid leg_id"):
            validate_leg_id(123)


class TestMomentumValidation:
    """Test momentum validation."""

    def test_valid_momentum_numpy(self):
        """Test valid numpy momentum array."""
        momentum = np.array([1.0, 0.5, 1.0, 0.0], dtype=np.float32)
        validate_momentum(momentum)

    def test_valid_momentum_list(self):
        """Test valid list momentum."""
        momentum = [1.0, 0.5, 1.0, 0.0]
        validate_momentum(momentum)

    def test_invalid_momentum_too_short(self):
        """Test momentum array too short."""
        momentum = np.array([1.0, 0.5], dtype=np.float32)
        with pytest.raises(ValidationError, match="Invalid momentum length"):
            validate_momentum(momentum)

    def test_invalid_momentum_type(self):
        """Test invalid momentum type."""
        with pytest.raises(ValidationError, match="Invalid momentum type"):
            validate_momentum("invalid")


class TestPositiveNumberValidation:
    """Test positive number validation."""

    def test_valid_positive_number(self):
        """Test valid positive numbers."""
        validate_positive_number(1)
        validate_positive_number(0.5)
        validate_positive_number(100)

    def test_invalid_negative_number(self):
        """Test negative number."""
        with pytest.raises(ValidationError, match="Invalid"):
            validate_positive_number(-1)

    def test_custom_min_value(self):
        """Test custom minimum value."""
        validate_positive_number(5, min_value=1)
        with pytest.raises(ValidationError):
            validate_positive_number(0.5, min_value=1)

