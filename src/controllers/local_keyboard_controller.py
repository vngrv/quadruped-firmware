# Note that this library requires sudo privileges

import keyboard
from src.utils.logger import get_logger
from src.utils.exceptions import ValidationError
from src.utils.validators import validate_positive_number

logger = get_logger(__name__)


def controller(momentum, accel=0.01, bound=4):
    """
    Update the momentum of the robot based on keyboard presses.

    Args:
        momentum: The existing momentum parameter [x, z, y, quit]
        accel: How quickly the robot starts walking in a given direction
        bound: The max/min magnitude that the robot can walk at

    Returns:
        Updated momentum array

    Raises:
        ValidationError: If parameters are invalid
    """
    # Validate parameters
    validate_positive_number(accel, "accel", min_value=0.0001)
    if accel > 1:
        raise ValidationError(f"Invalid accel value: {accel}. Must be <= 1")
    validate_positive_number(bound, "bound")

    try:
        if keyboard.is_pressed('w'):
            momentum[0] = min(momentum[0] + accel, bound)
            logger.debug("Forward key pressed")
        if keyboard.is_pressed('s'):
            momentum[0] = max(momentum[0] - accel, -bound)
            logger.debug("Backward key pressed")
        if keyboard.is_pressed('a'):
            momentum[1] = max(momentum[1] - accel, -bound)
            logger.debug("Left key pressed")
        if keyboard.is_pressed('d'):
            momentum[1] = min(momentum[1] + accel, bound)
            logger.debug("Right key pressed")
    except Exception as e:
        logger.error(f"Keyboard controller error: {e}", exc_info=True)

    return momentum


if __name__ == "__main__":
    import numpy as np

    momentum = np.asarray([0, 0, 1], dtype=np.float32)
    logger.info("Starting keyboard controller test")
    try:
        while True:
            momentum = controller(momentum)
            logger.debug(f"Current momentum: {momentum}")
    except KeyboardInterrupt:
        logger.info("Keyboard controller test stopped")
