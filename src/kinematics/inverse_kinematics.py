"""Inverse kinematics calculations for quadruped legs."""

import math
import numpy as np
from typing import Tuple, Optional

from src.utils.logger import get_logger
from src.utils.exceptions import KinematicsError, ValidationError
from src.utils.validators import validate_coordinate

logger = get_logger(__name__)


class InverseKinematics:
    """
    Inverse kinematics solver for quadruped robot legs.

    Calculates joint angles from desired end-effector positions.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize inverse kinematics solver.

        Args:
            config: Configuration dictionary with leg parameters
        """
        config = config.get('robot', {}) if config else {}
        legs_config = config.get('legs', {})
        offsets_config = config.get('offsets', {})
        kinematics_config = config.get('kinematics', {})

        self.upper_leg_length = legs_config.get('upper_length', 10.0)
        self.lower_leg_length = legs_config.get('lower_length', 10.5)
        self.shoulder_offset = offsets_config.get('shoulder', 10.0)
        self.elbow_offset = offsets_config.get('elbow', 20.0)
        self.hip_offset = offsets_config.get('hip', 0.0)
        self.hip_parameter = kinematics_config.get('hip_offset', 2.0)

        logger.debug(
            f"InverseKinematics initialized: "
            f"upper={self.upper_leg_length}, lower={self.lower_leg_length}"
        )

    def calculate(
        self,
        x: float,
        y: float,
        z: float = 0.0,
        hip_offset: Optional[float] = None,
        right: bool = True
    ) -> Tuple[float, float]:
        """
        Calculate joint angles for desired end-effector position.

        Args:
            x: X coordinate (forward/backward) in cm
            y: Y coordinate (up/down) in cm
            z: Z coordinate (left/right) in cm
            hip_offset: Optional hip offset parameter (L in original code)
            right: True for right side, False for left side

        Returns:
            Tuple of (shoulder_angle, elbow_angle) in degrees

        Raises:
            ValidationError: If coordinates are invalid
            KinematicsError: If position is unreachable
        """
        # Validate inputs
        validate_coordinate(x, "x")
        validate_coordinate(y, "y")
        validate_coordinate(z, "z")
        
        if y < 0.1:
            raise ValidationError(f"Y coordinate too small: {y}. Must be >= 0.1")

        # Use provided hip_offset or default
        hip_offset = hip_offset if hip_offset is not None else self.hip_parameter

        # Adjust for left/right side
        if not right:
            z = -z

        # Calculate distances
        upper_link_length = self.upper_leg_length
        lower_link_length = self.lower_leg_length

        # Distance from hip to end-effector
        distance_xy = math.sqrt(x * x + y * y)
        distance_xyz = math.sqrt(distance_xy * distance_xy + z * z)

        # Check reachability
        max_reach = upper_link_length + lower_link_length
        if distance_xyz > max_reach:
            raise KinematicsError(
                f"Position unreachable: distance={distance_xyz:.2f}cm, "
                f"max_reach={max_reach:.2f}cm"
            )

        # Calculate angles using law of cosines
        # Angle between upper and lower links
        cos_elbow = (
            (upper_link_length * upper_link_length +
             lower_link_length * lower_link_length -
             distance_xyz * distance_xyz) /
            (2 * upper_link_length * lower_link_length)
        )

        # Clamp to valid range for acos
        cos_elbow = max(-1.0, min(1.0, cos_elbow))
        elbow_angle_rad = math.acos(cos_elbow)

        # Angle of upper link relative to horizontal
        cos_shoulder = (
            (upper_link_length * upper_link_length +
             distance_xyz * distance_xyz -
             lower_link_length * lower_link_length) /
            (2 * upper_link_length * distance_xyz)
        )
        cos_shoulder = max(-1.0, min(1.0, cos_shoulder))
        shoulder_angle_rad = math.acos(cos_shoulder)

        # Calculate hip angle
        hip_angle_rad = math.atan2(z, distance_xy)

        # Convert to degrees and apply offsets
        shoulder_angle = math.degrees(shoulder_angle_rad) + self.shoulder_offset
        elbow_angle = math.degrees(elbow_angle_rad) + self.elbow_offset
        hip_angle = math.degrees(hip_angle_rad) + self.hip_offset

        logger.debug(
            f"Calculated angles: shoulder={shoulder_angle:.2f}°, "
            f"elbow={elbow_angle:.2f}°, hip={hip_angle:.2f}°"
        )

        return shoulder_angle, elbow_angle, hip_angle

    @staticmethod
    def rad_to_degree(radians: float) -> float:
        """
        Convert radians to degrees.

        Args:
            radians: Angle in radians

        Returns:
            Angle in degrees
        """
        return math.degrees(radians)

