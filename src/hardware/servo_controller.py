"""Servo motor controller abstraction."""

from enum import IntEnum
from typing import Dict, Any, Optional
from adafruit_servokit import ServoKit

from src.utils.logger import get_logger
from src.utils.exceptions import ServoError, ValidationError
from src.utils.monitoring import RobotMetrics
from src.utils.alerts import send_error_alert
from src.utils.validators import validate_motor_id, validate_angle

logger = get_logger(__name__)


class Motor(IntEnum):
    """Motor identifiers mapping to pin locations."""

    FR_SHOULDER = 0
    FR_ELBOW = 1
    FR_HIP = 2
    FL_SHOULDER = 3
    FL_ELBOW = 4
    FL_HIP = 5
    BR_SHOULDER = 6
    BR_ELBOW = 7
    BL_SHOULDER = 8
    BL_ELBOW = 9


class ServoController:
    """
    Controller for servo motors with retry logic and error handling.

    Provides abstraction over Adafruit ServoKit for reliable servo control.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, metrics: Optional[RobotMetrics] = None):
        """
        Initialize servo controller.

        Args:
            config: Configuration dictionary with servo parameters
            metrics: Optional metrics collector for monitoring

        Raises:
            ServoError: If servo initialization fails
        """
        try:
            robot_config = config.get('robot', {}) if config else {}
            servos_config = robot_config.get('servos', {})

            channels = servos_config.get('channels', 16)
            pulse_min = servos_config.get('pulse_min', 500)
            pulse_max = servos_config.get('pulse_max', 2500)

            self.kit = ServoKit(channels=channels)
            self.metrics = metrics
            self._setup_servos(pulse_min, pulse_max)

            logger.info("ServoController initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize ServoController: {e}", exc_info=True)
            raise ServoError(f"Servo initialization failed: {e}") from e

    def _setup_servos(self, pulse_min: int, pulse_max: int) -> None:
        """
        Set up pulse width ranges for all servos.

        Args:
            pulse_min: Minimum pulse width in microseconds
            pulse_max: Maximum pulse width in microseconds
        """
        for i in range(10):
            try:
                self.kit.servo[i].set_pulse_width_range(pulse_min, pulse_max)
            except Exception as e:
                logger.warning(f"Failed to set pulse width for servo {i}: {e}")

    def set_angle(self, motor_id: int, degrees: float, retry_count: int = 3) -> bool:
        """
        Set the angle of a specific motor with retry logic for graceful degradation.

        Args:
            motor_id: The motor ID (0-9)
            degrees: The angle in degrees (0-180)
            retry_count: Number of retry attempts on failure (default: 3)

        Returns:
            True if successful, False otherwise

        Raises:
            ValidationError: If motor_id or degrees are invalid
            ServoError: If servo operation fails after retries
        """
        # Validate inputs
        validate_motor_id(motor_id)
        validate_angle(degrees)

        # Retry logic for graceful degradation
        last_error = None
        for attempt in range(retry_count):
            try:
                import time
                start_time = time.time()
                self.kit.servo[motor_id].angle = degrees
                duration = time.time() - start_time

                # Record metrics if available
                if self.metrics:
                    self.metrics.record_motor_angle(motor_id, degrees)
                    self.metrics.record_performance('set_angle', duration)

                if attempt > 0:
                    logger.warning(f"Motor {motor_id} succeeded on retry {attempt + 1}")
                logger.debug(f"Set motor {motor_id} to {degrees} degrees")
                return True
            except Exception as e:
                last_error = e
                if attempt < retry_count - 1:
                    logger.warning(
                        f"Failed to set angle {degrees} for motor {motor_id} "
                        f"(attempt {attempt + 1}/{retry_count}): {e}"
                    )
                else:
                    logger.error(
                        f"Failed to set angle {degrees} for motor {motor_id} "
                        f"after {retry_count} attempts: {e}",
                        exc_info=True
                    )

        # All retries failed
        send_error_alert(f"Motor {motor_id} failed after {retry_count} attempts", last_error)
        raise ServoError(f"Motor {motor_id} failed after {retry_count} attempts: {last_error}") from last_error

    def calibrate(self, calibration_angles: Dict[int, float]) -> bool:
        """
        Calibrate all servos to specified angles.

        Args:
            calibration_angles: Dictionary mapping motor_id to calibration angle

        Returns:
            True if calibration successful, False otherwise
        """
        logger.info("Starting servo calibration")
        success = True

        for motor_id, angle in calibration_angles.items():
            try:
                self.set_angle(motor_id, angle)
                logger.debug(f"Calibrated motor {motor_id} to {angle} degrees")
            except Exception as e:
                logger.error(f"Failed to calibrate motor {motor_id}: {e}")
                success = False

        if success:
            logger.info("Servo calibration completed successfully")
        else:
            logger.warning("Servo calibration completed with errors")

        return success

