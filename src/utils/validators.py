"""Input validation utilities for quadruped robot."""

from typing import Any, Union
from src.utils.exceptions import ValidationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


def validate_motor_id(motor_id: int) -> None:
    """
    Validate motor ID.

    Args:
        motor_id: Motor ID to validate

    Raises:
        ValidationError: If motor_id is invalid
    """
    if not isinstance(motor_id, int) or not (0 <= motor_id < 10):
        raise ValidationError(f"Invalid motor_id: {motor_id}. Must be integer in [0, 9]")


def validate_angle(angle: float, min_angle: float = 0.0, max_angle: float = 180.0) -> None:
    """
    Validate angle value.

    Args:
        angle: Angle to validate in degrees
        min_angle: Minimum allowed angle (default: 0.0)
        max_angle: Maximum allowed angle (default: 180.0)

    Raises:
        ValidationError: If angle is invalid
    """
    if not isinstance(angle, (int, float)):
        raise ValidationError(f"Invalid angle type: {type(angle)}. Must be numeric")
    
    if not (min_angle <= angle <= max_angle):
        raise ValidationError(
            f"Angle {angle} out of range [{min_angle}, {max_angle}]"
        )


def validate_coordinate(value: Any, name: str = "coordinate") -> None:
    """
    Validate coordinate value.

    Args:
        value: Coordinate value to validate
        name: Name of the coordinate for error messages

    Raises:
        ValidationError: If coordinate is invalid
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"Invalid {name}: {value}. Must be numeric")


def validate_leg_id(leg_id: str, valid_ids: tuple = ('FL', 'FR', 'BL', 'BR')) -> None:
    """
    Validate leg identifier.

    Args:
        leg_id: Leg ID to validate
        valid_ids: Tuple of valid leg IDs

    Raises:
        ValidationError: If leg_id is invalid
    """
    if not isinstance(leg_id, str) or leg_id not in valid_ids:
        raise ValidationError(
            f"Invalid leg_id: {leg_id}. Must be one of {valid_ids}"
        )


def validate_momentum(momentum: Any) -> None:
    """
    Validate momentum array.

    Args:
        momentum: Momentum array to validate

    Raises:
        ValidationError: If momentum is invalid
    """
    import numpy as np
    
    if not isinstance(momentum, (np.ndarray, list, tuple)):
        raise ValidationError(f"Invalid momentum type: {type(momentum)}")
    
    momentum_array = np.asarray(momentum)
    
    if len(momentum_array) < 4:
        raise ValidationError(
            f"Invalid momentum length: {len(momentum_array)}. Must be >= 4"
        )
    
    if momentum_array.dtype != np.float32:
        logger.warning(
            f"Momentum dtype is {momentum_array.dtype}, expected float32"
        )


def validate_positive_number(value: Any, name: str = "value", min_value: float = 0.0) -> None:
    """
    Validate positive number.

    Args:
        value: Value to validate
        name: Name of the value for error messages
        min_value: Minimum allowed value (default: 0.0)

    Raises:
        ValidationError: If value is invalid
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"Invalid {name} type: {type(value)}. Must be numeric")
    
    if value < min_value:
        raise ValidationError(f"Invalid {name}: {value}. Must be >= {min_value}")

