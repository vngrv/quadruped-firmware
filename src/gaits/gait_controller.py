"""Gait controller for applying trajectories to robot legs."""

import numpy as np
from typing import Optional

from src.hardware.servo_controller import Motor
from src.kinematics.inverse_kinematics import InverseKinematics
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GaitController:
    """
    Controller for applying gait trajectories to robot legs.

    Manages the application of trajectories to individual legs using trot gait.
    """

    def __init__(
        self,
        servo_controller,
        kinematics: InverseKinematics,
        step_resolution: int = 20
    ):
        """
        Initialize gait controller.

        Args:
            servo_controller: ServoController instance for motor control
            kinematics: InverseKinematics instance for calculations
            step_resolution: Number of points in step trajectory
        """
        self.servo_controller = servo_controller
        self.kinematics = kinematics
        self.step_resolution = step_resolution

    def apply_trajectory_to_leg(
        self,
        shoulder_motor: int,
        elbow_motor: int,
        x: float,
        y: float,
        z: float = 0.0,
        hip_motor: Optional[int] = None,
        right: bool = True
    ) -> None:
        """
        Apply trajectory point to a leg.

        Args:
            shoulder_motor: Motor ID for shoulder
            elbow_motor: Motor ID for elbow
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            hip_motor: Optional motor ID for hip
            right: True for right side, False for left
        """
        shoulder_angle, elbow_angle, hip_angle = self.kinematics.calculate(
            x, y, z, right=right
        )

        # Set shoulder and elbow angles
        self.servo_controller.set_angle(shoulder_motor, shoulder_angle)
        self.servo_controller.set_angle(elbow_motor, elbow_angle)

        # Set hip angle if provided
        if hip_motor is not None:
            self.servo_controller.set_angle(hip_motor, hip_angle)

    def apply_trot_gait_step(
        self,
        trajectory: np.ndarray,
        step_index: int,
        trajectory_length: int
    ) -> None:
        """
        Apply trot gait step to all legs.

        Args:
            trajectory: Trajectory array with shape (3, N) for (x, z, y) coordinates
            step_index: Current step index
            trajectory_length: Length of trajectory
        """
        x_coords, z_coords, y_coords = trajectory

        # Calculate indices for diagonal leg pairs
        index_1 = step_index % trajectory_length
        index_2 = (step_index + self.step_resolution) % trajectory_length

        # Pre-calculate coordinate values
        x1, y1, z1 = x_coords[index_1], y_coords[index_1], z_coords[index_1]
        x2, y2, z2 = x_coords[index_2], y_coords[index_2], z_coords[index_2]

        # Apply movement to legs (trot gait - diagonal pairs)
        # Front Right leg
        self.apply_trajectory_to_leg(
            Motor.FR_SHOULDER, Motor.FR_ELBOW,
            x1, y1 - 1, z=z1,
            hip_motor=Motor.FR_HIP, right=True
        )

        # Back Right leg
        self.apply_trajectory_to_leg(
            Motor.BR_SHOULDER, Motor.BR_ELBOW,
            x2, y2 + 2,
            right=True
        )

        # Front Left leg
        self.apply_trajectory_to_leg(
            Motor.FL_SHOULDER, Motor.FL_ELBOW,
            x2, y2 - 1, z=-z2,
            hip_motor=Motor.FL_HIP, right=False
        )

        # Back Left leg
        self.apply_trajectory_to_leg(
            Motor.BL_SHOULDER, Motor.BL_ELBOW,
            x1, y1 + 2,
            right=False
        )

