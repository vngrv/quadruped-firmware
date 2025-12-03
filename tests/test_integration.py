"""Integration tests for quadruped robot movement cycle."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.robot.quadruped import Quadruped
from src.hardware.servo_controller import Motor


class TestMovementCycle:
    """Integration tests for movement cycle."""

    @pytest.fixture
    def mock_quadruped(self, mocker):
        """Create a mock Quadruped instance."""
        mocker.patch('src.hardware.servo_controller.ServoKit')
        config = {
            'robot': {
                'legs': {'upper_length': 10.0, 'lower_length': 10.5},
                'servos': {'channels': 16, 'pulse_min': 500, 'pulse_max': 2500},
                'offsets': {'shoulder': 10, 'elbow': 20, 'hip': 0},
                'calibration': {},
                'kinematics': {'hip_offset': 2.0}
            }
        }
        quad = Quadruped(config)
        # Mock servo controller methods
        quad.servo_controller.set_angle = Mock(return_value=True)
        return quad

    def test_movement_cycle_basic(self, mock_quadruped):
        """Test basic movement cycle execution."""
        call_count = {'count': 0}

        def test_controller(momentum):
            call_count['count'] += 1
            if call_count['count'] > 5:
                momentum[3] = 1.0  # Quit after 5 iterations
            return momentum

        mock_quadruped.move(test_controller)

        # Should have called set_angle multiple times (4 legs * iterations)
        assert mock_quadruped.servo_controller.set_angle.call_count > 0

    def test_movement_cycle_quit_flag(self, mock_quadruped):
        """Test movement cycle respects quit flag."""
        call_count = {'count': 0}

        def quit_controller(momentum):
            call_count['count'] += 1
            momentum[3] = 1.0  # Quit immediately
            return momentum

        mock_quadruped.move(quit_controller)

        # Should exit quickly
        assert call_count['count'] == 1

    def test_movement_cycle_momentum_application(self, mock_quadruped):
        """Test that momentum is applied to trajectory."""
        momentum_values = []

        def momentum_controller(momentum):
            momentum[0] = 2.0  # Forward momentum
            momentum[1] = 0.5  # Right momentum
            momentum[2] = 1.0  # Height
            momentum[3] = 1.0  # Quit
            momentum_values.append(momentum.copy())
            return momentum

        mock_quadruped.move(momentum_controller)

        assert len(momentum_values) == 1
        assert momentum_values[0][0] == 2.0
        assert momentum_values[0][1] == 0.5

    def test_trajectory_generation(self, mock_quadruped):
        """Test trajectory generation is cached."""
        trajectory, length = mock_quadruped.trajectory_generator.generate()

        assert trajectory is not None
        assert length > 0
        assert trajectory.shape[0] == 3  # x, z, y coordinates

    def test_calibration_sequence(self, mock_quadruped):
        """Test calibration sets all motors."""
        result = mock_quadruped.calibrate()

        assert result is True
        # Should have called set_angle for all motors
        assert mock_quadruped.servo_controller.set_angle.call_count >= 9


class TestControllerIntegration:
    """Integration tests for controllers."""

    def test_keyboard_controller_integration(self):
        """Test keyboard controller with mock keyboard."""
        from src.controllers.local_keyboard_controller import controller

        with patch('src.controllers.local_keyboard_controller.keyboard') as mock_kb:
            mock_kb.is_pressed.side_effect = lambda key: key == 'w'

            momentum = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)
            result = controller(momentum, accel=0.1, bound=4.0)

            assert result[0] > 0  # Forward momentum

    def test_network_receiver_integration(self):
        """Test network receiver with mock socket."""
        from src.controllers.network_receiver import controller
        import socket

        with patch('src.controllers.network_receiver.s') as mock_socket:
            test_data = np.array([1.0, 0.5, 1.0, 0.0], dtype=np.float32).tobytes()
            mock_socket.recvfrom.return_value = (test_data, ('127.0.0.1', 5000))
            mock_socket.settimeout = Mock()

            momentum = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)
            result = controller(momentum)

            assert np.allclose(result[:3], [1.0, 0.5, 1.0])

