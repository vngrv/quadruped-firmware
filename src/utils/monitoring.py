"""Monitoring and metrics utilities for quadruped robot."""

import time
from typing import Dict, List, Optional
from collections import deque
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RobotMetrics:
    """Collects and stores robot metrics."""

    def __init__(self, history_size: int = 1000):
        """
        Initialize metrics collector.

        Args:
            history_size: Maximum number of entries to keep in history
        """
        self.history_size = history_size
        self.motor_angles: Dict[int, float] = {}
        self.controller_status: Dict[str, bool] = {}
        self.movement_history: deque = deque(maxlen=history_size)
        self.performance_metrics: deque = deque(maxlen=history_size)
        self.error_count: int = 0
        self.start_time = time.time()

    def record_motor_angle(self, motor_id: int, angle: float) -> None:
        """
        Record motor angle.

        Args:
            motor_id: Motor ID
            angle: Angle in degrees
        """
        self.motor_angles[motor_id] = angle

    def record_controller_status(self, controller_name: str, is_available: bool) -> None:
        """
        Record controller status.

        Args:
            controller_name: Name of the controller
            is_available: Whether controller is available
        """
        self.controller_status[controller_name] = is_available

    def record_movement(self, momentum: List[float], trajectory: Optional[List] = None) -> None:
        """
        Record movement command.

        Args:
            momentum: Momentum array [x, z, y, quit]
            trajectory: Optional trajectory data
        """
        entry = {
            'timestamp': time.time(),
            'momentum': momentum.copy() if hasattr(momentum, 'copy') else list(momentum),
            'trajectory': trajectory
        }
        self.movement_history.append(entry)

    def record_performance(self, operation: str, duration: float) -> None:
        """
        Record performance metric.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
        """
        entry = {
            'timestamp': time.time(),
            'operation': operation,
            'duration': duration
        }
        self.performance_metrics.append(entry)

    def record_error(self) -> None:
        """Record an error occurrence."""
        self.error_count += 1

    def get_motor_angles(self) -> Dict[int, float]:
        """
        Get current motor angles.

        Returns:
            Dictionary mapping motor_id to angle
        """
        return self.motor_angles.copy()

    def get_controller_status(self) -> Dict[str, bool]:
        """
        Get controller status.

        Returns:
            Dictionary mapping controller name to availability
        """
        return self.controller_status.copy()

    def get_movement_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get movement history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of movement entries
        """
        history = list(self.movement_history)
        if limit:
            return history[-limit:]
        return history

    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get performance statistics.

        Returns:
            Dictionary with performance statistics:
            - avg_duration: Average operation duration in seconds
            - min_duration: Minimum operation duration in seconds
            - max_duration: Maximum operation duration in seconds
            - total_operations: Total number of operations recorded
        """
        if not self.performance_metrics:
            return {}

        durations = [m['duration'] for m in self.performance_metrics]
        return {
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'total_operations': len(self.performance_metrics)
        }

    def get_uptime(self) -> float:
        """
        Get system uptime.

        Returns:
            Uptime in seconds
        """
        return time.time() - self.start_time

    def get_summary(self) -> Dict:
        """
        Get summary of all metrics.

        Returns:
            Dictionary with summary metrics
        """
        return {
            'uptime': self.get_uptime(),
            'motor_angles': self.get_motor_angles(),
            'controller_status': self.get_controller_status(),
            'movement_count': len(self.movement_history),
            'error_count': self.error_count,
            'performance': self.get_performance_stats()
        }

