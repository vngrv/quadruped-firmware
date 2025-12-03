"""Tests for controller modules."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.utils.exceptions import ValidationError, ControllerError


class TestKeyboardController:
    """Test keyboard controller."""

    @patch('controllers.local_keyboard_controller.keyboard')
    def test_controller_forward(self, mock_keyboard):
        """Test forward movement."""
        from controllers.local_keyboard_controller import controller

        mock_keyboard.is_pressed.side_effect = lambda key: key == 'w'
        momentum = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)

        result = controller(momentum, accel=0.1, bound=4.0)
        assert result[0] > 0  # Forward momentum increased

    @patch('controllers.local_keyboard_controller.keyboard')
    def test_controller_backward(self, mock_keyboard):
        """Test backward movement."""
        from controllers.local_keyboard_controller import controller

        mock_keyboard.is_pressed.side_effect = lambda key: key == 's'
        momentum = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)

        result = controller(momentum, accel=0.1, bound=4.0)
        assert result[0] < 0  # Backward momentum

    @patch('controllers.local_keyboard_controller.keyboard')
    def test_controller_bounds(self, mock_keyboard):
        """Test momentum bounds."""
        from controllers.local_keyboard_controller import controller

        mock_keyboard.is_pressed.side_effect = lambda key: key == 'w'
        momentum = np.array([4.0, 0.0, 1.0, 0.0], dtype=np.float32)  # Already at bound

        result = controller(momentum, accel=0.1, bound=4.0)
        assert result[0] == 4.0  # Should not exceed bound

    def test_controller_invalid_accel(self):
        """Test invalid acceleration parameter."""
        from controllers.local_keyboard_controller import controller

        momentum = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)
        with pytest.raises(ValidationError, match="Invalid accel"):
            controller(momentum, accel=-1, bound=4)

    def test_controller_invalid_bound(self):
        """Test invalid bound parameter."""
        from controllers.local_keyboard_controller import controller

        momentum = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)
        with pytest.raises(ValidationError, match="Invalid bound"):
            controller(momentum, accel=0.1, bound=-1)


class TestNetworkReceiver:
    """Test network receiver controller."""

    @patch('src.controllers.network_receiver.s')
    def test_controller_receives_data(self, mock_socket):
        """Test receiving valid data."""
        from src.controllers.network_receiver import controller

        # Mock socket receive
        test_data = np.array([1.0, 0.5, 1.0, 0.0], dtype=np.float32).tobytes()
        mock_socket.recvfrom.return_value = (test_data, ('192.168.1.1', 5000))
        mock_socket.settimeout = Mock()

        momentum = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)
        result = controller(momentum)

        assert np.allclose(result[:3], [1.0, 0.5, 1.0])

    @patch('src.controllers.network_receiver.s')
    def test_controller_timeout(self, mock_socket):
        """Test timeout handling."""
        import socket
        from src.controllers.network_receiver import controller

        mock_socket.recvfrom.side_effect = socket.timeout()
        mock_socket.settimeout = Mock()

        momentum = np.array([1.0, 0.5, 1.0, 0.0], dtype=np.float32)
        result = controller(momentum)

        # Should return original momentum on timeout
        assert np.allclose(result, momentum)

    @patch('src.controllers.network_receiver.s')
    def test_controller_incomplete_data(self, mock_socket):
        """Test handling of incomplete data."""
        from src.controllers.network_receiver import controller

        # Incomplete data (less than 16 bytes)
        mock_socket.recvfrom.return_value = (b'\x00' * 8, ('192.168.1.1', 5000))
        mock_socket.settimeout = Mock()

        momentum = np.array([1.0, 0.5, 1.0, 0.0], dtype=np.float32)
        result = controller(momentum)

        # Should return original momentum
        assert np.allclose(result, momentum)

    @patch('src.controllers.network_receiver.s')
    def test_controller_consecutive_errors(self, mock_socket):
        """Test handling of consecutive errors."""
        import socket
        from src.controllers.network_receiver import controller

        # Simulate consecutive errors
        mock_socket.recvfrom.side_effect = socket.error("Connection failed")
        mock_socket.settimeout = Mock()

        momentum = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)

        # First few errors should be handled gracefully
        for i in range(9):
            result = controller(momentum)
            assert result is not None

        # 10th error should raise exception
        with pytest.raises(ControllerError):
            controller(momentum)

