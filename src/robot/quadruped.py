"""Main Quadruped robot controller using modular architecture."""

import time
import numpy as np
from typing import Optional, Dict, Any, Callable, List

from src.hardware.servo_controller import ServoController, Motor
from src.kinematics.inverse_kinematics import InverseKinematics
from src.gaits.trajectory_generator import TrajectoryGenerator
from src.gaits.gait_controller import GaitController
from src.utils.logger import get_logger
from src.utils.monitoring import RobotMetrics
from src.utils.alerts import send_critical_alert

logger = get_logger(__name__)


class Quadruped:
    """
    Quadruped robot controller with modular architecture.

    Coordinates hardware control, kinematics, and gait generation.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the quadruped robot.

        Args:
            config: Configuration dictionary with robot parameters.
                   If None, uses default values.

        Raises:
            ServoError: If servo initialization fails
        """
        try:
            # Initialize metrics collector
            self.metrics = RobotMetrics()

            # Initialize hardware layer
            self.servo_controller = ServoController(config, self.metrics)

            # Initialize kinematics
            self.kinematics = InverseKinematics(config)

            # Initialize gait components
            step_resolution = 20
            self.trajectory_generator = TrajectoryGenerator(step_resolution)
            self.gait_controller = GaitController(
                self.servo_controller,
                self.kinematics,
                step_resolution
            )

            # Store calibration angles
            robot_config = config.get('robot', {}) if config else {}
            self.calibration_angles = robot_config.get(
                'calibration',
                self._default_calibration()
            )

            logger.info("Quadruped initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Quadruped: {e}", exc_info=True)
            send_critical_alert("Quadruped initialization failed", e)
            raise

    def _default_calibration(self) -> Dict[str, float]:
        """Get default calibration angles."""
        return {
            'FR_SHOULDER': 60,
            'FR_ELBOW': 90,
            'FR_HIP': 90,
            'FL_SHOULDER': 120,
            'FL_ELBOW': 90,
            'FL_HIP': 90,
            'BR_SHOULDER': 60,
            'BR_ELBOW': 90,
            'BL_SHOULDER': 120,
            'BL_ELBOW': 90,
        }

    def calibrate(self) -> bool:
        """
        Calibrate robot to default position.

        Returns:
            True if calibration successful, False otherwise
        """
        logger.info("Starting robot calibration")

        # Convert calibration angles to motor IDs
        calibration_dict = {}
        for motor_name, angle in self.calibration_angles.items():
            try:
                motor_id = Motor[motor_name].value
                calibration_dict[motor_id] = angle
            except KeyError:
                logger.warning(f"Unknown motor name in calibration: {motor_name}")

        success = self.servo_controller.calibrate(calibration_dict)
        return success

    def leg_position(self, leg_id: str, x: float, y: float, z: float = 0.0) -> bool:
        """
        Set position of a specific leg.

        Args:
            leg_id: Leg identifier ('FL', 'FR', 'BL', 'BR')
            x: X coordinate (forward/backward) in cm
            y: Y coordinate (up/down) in cm
            z: Z coordinate (left/right) in cm

        Returns:
            True if successful, False otherwise

        Raises:
            ValidationError: If leg_id is invalid
        """
        from src.utils.validators import validate_leg_id, validate_coordinate

        # Validate inputs
        validate_leg_id(leg_id)
        validate_coordinate(x, "x")
        validate_coordinate(y, "y")
        validate_coordinate(z, "z")

        leg_mapping = {
            'FR': (Motor.FR_SHOULDER, Motor.FR_ELBOW, Motor.FR_HIP, True),
            'FL': (Motor.FL_SHOULDER, Motor.FL_ELBOW, Motor.FL_HIP, False),
            'BR': (Motor.BR_SHOULDER, Motor.BR_ELBOW, None, True),
            'BL': (Motor.BL_SHOULDER, Motor.BL_ELBOW, None, False),
        }

        shoulder_motor, elbow_motor, hip_motor, right = leg_mapping[leg_id]

        try:
            self.gait_controller.apply_trajectory_to_leg(
                shoulder_motor, elbow_motor, x, y, z,
                hip_motor=hip_motor, right=right
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set leg {leg_id} position: {e}", exc_info=True)
            return False

    def move(self, controller: Optional[Callable] = None) -> None:
        """
        Main movement loop that walks based on controller input.

        Args:
            controller: Controller function that returns momentum array [x, z, y, quit]

        Returns:
            None (enters infinite loop until quit flag is set)
        """
        if controller is None:
            logger.error("No controller provided")
            return

        logger.info("Starting movement loop")
        momentum = np.asarray([0.0, 0.0, 1.0, 0.0], dtype=np.float32)
        step_index = 0
        cycle_count = 0

        # Generate trajectory once (cached)
        motion_trajectory, trajectory_length = self.trajectory_generator.generate()
        logger.debug(f"Generated trajectory with {trajectory_length} points")

        try:
            while True:
                cycle_start = time.time()

                # Get momentum from controller
                momentum = controller(momentum)

                # Record controller status
                self.metrics.record_controller_status('active_controller', True)

                # Check quit flag
                if momentum[3] > 0.5:
                    logger.info("Shutdown signal received")
                    break

                # Apply momentum to trajectory
                momentum_3d = momentum[:3, None]
                x_coords = motion_trajectory[0] * momentum_3d[0]
                z_coords = motion_trajectory[1] * momentum_3d[1]
                y_coords = motion_trajectory[2] * momentum_3d[2]

                # Combine into trajectory array
                trajectory = np.array([x_coords, z_coords, y_coords])

                # Record movement
                self.metrics.record_movement(
                    momentum.tolist(),
                    trajectory=[x_coords.tolist(), z_coords.tolist(), y_coords.tolist()]
                )

                # Apply trot gait step
                self.gait_controller.apply_trot_gait_step(
                    trajectory, step_index, trajectory_length
                )

                step_index += 1
                cycle_count += 1

                # Record performance
                cycle_duration = time.time() - cycle_start
                self.metrics.record_performance('movement_cycle', cycle_duration)

                # Log metrics periodically
                if cycle_count % 100 == 0:
                    perf_stats = self.metrics.get_performance_stats()
                    logger.debug(
                        f"Cycle {cycle_count}: avg_duration={perf_stats.get('avg_duration', 0):.4f}s, "
                        f"errors={self.metrics.error_count}"
                    )

        except KeyboardInterrupt:
            logger.info("Movement interrupted by user")
            self._log_final_metrics(cycle_count)
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Movement loop error: {e}", exc_info=True)
            self._log_final_metrics(cycle_count)
            raise

    def _log_final_metrics(self, cycle_count: int) -> None:
        """
        Log final metrics summary.

        Args:
            cycle_count: Total number of cycles executed
        """
        summary = self.metrics.get_summary()
        logger.info(
            f"Movement completed: cycles={cycle_count}, "
            f"uptime={summary['uptime']:.2f}s, "
            f"errors={summary['error_count']}"
        )
        if summary['performance']:
            perf = summary['performance']
            logger.info(
                f"Performance: avg={perf.get('avg_duration', 0):.4f}s, "
                f"min={perf.get('min_duration', 0):.4f}s, "
                f"max={perf.get('max_duration', 0):.4f}s"
            )

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current robot metrics.

        Returns:
            Dictionary with current metrics including:
            - uptime: System uptime in seconds
            - motor_angles: Current motor angles
            - controller_status: Controller availability
            - movement_count: Number of movements recorded
            - error_count: Total error count
            - performance: Performance statistics
        """
        return self.metrics.get_summary()

