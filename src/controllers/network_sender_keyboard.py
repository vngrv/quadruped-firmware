import socket
import numpy as np
import argparse
import keyboard

from src.controllers.utils.ip_helper import create_socket_connection
from src.utils.logger import get_logger
from src.utils.exceptions import ControllerError, ValidationError
from src.utils.validators import validate_positive_number

logger = get_logger(__name__)


def controller(pi_ip, pi_port, accel=0.002, bound=4, return_to_zero=False):
    """
    Network sender controller that sends keyboard commands via UDP.

    Args:
        pi_ip: Raspberry Pi IP address
        pi_port: Raspberry Pi port
        accel: Acceleration value (how quickly robot starts walking)
        bound: Maximum/minimum magnitude for movement
        return_to_zero: If True, slowly return to zero when not controlling

    Raises:
        ValidationError: If parameters are invalid
        ControllerError: If network operations fail
    """
    # Validate parameters
    validate_positive_number(accel, "accel", min_value=0.0001)
    if accel > 1:
        raise ValidationError(f"Invalid accel value: {accel}. Must be <= 1")
    validate_positive_number(bound, "bound")

    try:
        s = create_socket_connection()
        server = (pi_ip, pi_port)
        momentum = np.array([0., 0., 1., 0.])  # Control [x,z,y,quit] telemetry
        close = False

        logger.info(f"Network sender controller started. Target: {server}")

        while not close:
            moved = False
            try:
                if keyboard.is_pressed('w'):
                    momentum[0] = min(momentum[0] + accel, bound)
                    moved = True
                if keyboard.is_pressed('s'):
                    momentum[0] = max(momentum[0] - accel, -bound)
                    moved = True
                if keyboard.is_pressed('a'):
                    momentum[1] = max(momentum[1] - accel, -bound)
                    moved = True
                if keyboard.is_pressed('d'):
                    momentum[1] = min(momentum[1] + accel, bound)
                    moved = True
                if keyboard.is_pressed('p'):
                    momentum[3] = 1
                    close = True
                    moved = True
                    logger.info("Quit key pressed")

                # Not controlling the robot will slowly come to a stop
                if return_to_zero and not moved:
                    moved = True
                    if momentum[0] > 0:
                        momentum[0] = momentum[0] - accel
                    elif momentum[0] < 0:
                        momentum[0] = momentum[0] + accel
                    if momentum[1] > 0:
                        momentum[1] = momentum[1] - accel
                    elif momentum[1] < 0:
                        momentum[1] = momentum[1] + accel

                if moved:
                    s.sendto(momentum.tobytes(), server)
                    logger.debug(f"Sent momentum: {momentum}")

            except keyboard.KeyboardInterrupt:
                logger.info("Interrupted by user")
                close = True
            except Exception as e:
                logger.error(f"Error in controller loop: {e}", exc_info=True)

        s.close()
        logger.info("Network sender controller stopped")

    except Exception as e:
        logger.error(f"Network sender controller failed: {e}", exc_info=True)
        raise ControllerError(f"Network sender failed: {e}") from e


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pi_ip')
    parser.add_argument('pi_port', type=int)
    parser.add_argument('--accel', type=float, default=0.002)
    parser.add_argument('--bound', type=int, default=4)
    parser.add_argument('--return_to_zero', action='store_true')
    args = parser.parse_args()

    controller(args.pi_ip, args.pi_port, args.accel,
               args.bound, args.return_to_zero)
