"""Tests for inverse kinematics calculations."""

import pytest
import numpy as np
from src.robot.quadruped import Quadruped
from src.hardware.servo_controller import Motor
from src.kinematics.inverse_kinematics import InverseKinematics
from src.utils.exceptions import KinematicsError


class TestInverseKinematics:
    """Test inverse kinematics calculations."""

    @pytest.fixture
    def mock_quadruped(self, mocker):
        """Create a mock Quadruped instance."""
        mocker.patch('src.hardware.servo_controller.ServoKit')
        config = {
            'robot': {
                'legs': {'upper_length': 10.0, 'lower_length': 10.5},
                'servos': {'channels': 16, 'pulse_min': 500, 'pulse_max': 2500},
                'offsets': {'shoulder': 10, 'elbow': 20, 'hip': 0},
                'kinematics': {'hip_offset': 2.0},
                'calibration': {}
            }
        }
        quad = Quadruped(config)
        # Mock set_angle to avoid actual hardware calls
        quad.set_angle = lambda motor_id, degrees: True
        return quad

    def test_kinematics_reachable_position(self):
        """Test kinematics with reachable position."""
        config = {
            'robot': {
                'legs': {'upper_length': 10.0, 'lower_length': 10.5},
                'offsets': {'shoulder': 10, 'elbow': 20, 'hip': 0},
                'kinematics': {'hip_offset': 2.0}
            }
        }
        kinematics = InverseKinematics(config)
        shoulder, elbow, hip = kinematics.calculate(5, -15, z=0, right=True)
        assert isinstance(shoulder, (int, float))
        assert isinstance(elbow, (int, float))
        assert isinstance(hip, (int, float))

    def test_kinematics_unreachable_position(self):
        """Test kinematics with unreachable position."""
        config = {
            'robot': {
                'legs': {'upper_length': 10.0, 'lower_length': 10.5},
                'offsets': {'shoulder': 10, 'elbow': 20, 'hip': 0},
                'kinematics': {'hip_offset': 2.0}
            }
        }
        kinematics = InverseKinematics(config)
        # Position too far away
        with pytest.raises(KinematicsError, match="Position unreachable"):
            kinematics.calculate(50, -15, z=0, right=True)

    def test_rad_to_degree_conversion(self):
        """Test radians to degrees conversion."""
        assert abs(InverseKinematics.rad_to_degree(np.pi) - 180) < 0.01
        assert abs(InverseKinematics.rad_to_degree(np.pi / 2) - 90) < 0.01
        assert abs(InverseKinematics.rad_to_degree(0) - 0) < 0.01

