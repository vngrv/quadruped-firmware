"""Trajectory generation using Bezier curves."""

import bezier
import numpy as np
from typing import Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TrajectoryGenerator:
    """
    Generates gait trajectories using Bezier curves.

    Creates smooth foot trajectories for walking gaits.
    """

    def __init__(self, step_resolution: int = 20):
        """
        Initialize trajectory generator.

        Args:
            step_resolution: Number of points in step trajectory
        """
        self.step_resolution = step_resolution
        self._cached_trajectory = None
        self._cached_length = None

    def generate(self) -> Tuple[np.ndarray, int]:
        """
        Generate gait trajectory using Bezier curves (cached).

        Returns:
            Tuple of (motion_trajectory, trajectory_length)
        """
        if self._cached_trajectory is not None:
            return self._cached_trajectory, self._cached_length

        s_vals = np.linspace(0.0, 1.0, self.step_resolution)

        # Step trajectory (lifting foot)
        step_nodes = np.asfortranarray([
            [-1.0, -1.0, 1.0, 1.0],
            [-1.0, -1.0, 1.0, 1.0],
            [-15.0, -10, -10, -15.0],
        ])
        step_curve = bezier.Curve(step_nodes, degree=3)
        step_trajectory = step_curve.evaluate_multi(s_vals)

        # Slide trajectory (sliding foot)
        slide_nodes = np.asfortranarray([
            [1.0, -1.0],
            [1.0, -1.0],
            [-15.0, -15],
        ])
        slide_curve = bezier.Curve(slide_nodes, degree=1)
        slide_trajectory = slide_curve.evaluate_multi(s_vals)

        # Combined motion trajectory
        motion_trajectory = np.concatenate((step_trajectory, slide_trajectory), axis=1)
        trajectory_length = len(motion_trajectory[0])

        self._cached_trajectory = motion_trajectory
        self._cached_length = trajectory_length

        logger.debug(f"Generated trajectory with {trajectory_length} points")
        return motion_trajectory, trajectory_length

    def clear_cache(self) -> None:
        """Clear cached trajectory."""
        self._cached_trajectory = None
        self._cached_length = None

