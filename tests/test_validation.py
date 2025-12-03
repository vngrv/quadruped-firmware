"""Tests for input validation."""

import pytest
import numpy as np
from src.utils.exceptions import ValidationError, ServoError
from src.robot.quadruped import Quadruped
from src.hardware.servo_controller import Motor


class TestQuadrupedValidation:
    """Test validation in Quadruped class."""

    @pytest.fixture
    def mock_quadruped(self, mocker):
        """Create a mock Quadruped instance."""
        mocker.patch('src.hardware.servo_controller.ServoKit')
        config = {
            'robot': {
                'legs': {'upper_length': 10.0, 'lower_length': 10.5},
                'servos': {'channels': 16, 'pulse_min': 500, 'pulse_max': 2500},
                'offsets': {'shoulder': 10, 'elbow': 20, 'hip': 0},
                'calibration': {}
            }
        }
        return Quadruped(config)

    def test_set_angle_invalid_motor_id(self, mock_quadruped):
        """Test set_angle with invalid motor_id."""
        with pytest.raises(ValidationError, match="Invalid motor_id"):
            mock_quadruped.servo_controller.set_angle(-1, 90)

        with pytest.raises(ValidationError, match="Invalid motor_id"):
            mock_quadruped.servo_controller.set_angle(10, 90)

    def test_set_angle_invalid_angle(self, mock_quadruped):
        """Test set_angle with invalid angle."""
        with pytest.raises(ValidationError, match="out of range"):
            mock_quadruped.servo_controller.set_angle(0, -1)

        with pytest.raises(ValidationError, match="out of range"):
            mock_quadruped.servo_controller.set_angle(0, 181)

    def test_leg_position_invalid_leg_id(self, mock_quadruped):
        """Test leg_position with invalid leg_id."""
        with pytest.raises(ValidationError, match="Invalid leg_id"):
            mock_quadruped.leg_position('XX', 0, -15)

    def test_inverse_positioning_invalid_coordinates(self, mock_quadruped):
        """Test inverse_positioning with invalid coordinates."""
        from src.kinematics.inverse_kinematics import InverseKinematics
        kinematics = mock_quadruped.kinematics
        
        with pytest.raises(ValidationError, match="Invalid coordinates"):
            kinematics.calculate("invalid", 10)

        with pytest.raises(ValidationError, match="Y coordinate too small"):
            kinematics.calculate(5, 0.05)

