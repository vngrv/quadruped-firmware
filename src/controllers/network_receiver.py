import numpy as np
import socket

from src.controllers.utils.ip_helper import create_socket_connection
from src.utils.logger import get_logger
from src.utils.exceptions import ControllerError, ValidationError
from src.utils.validators import validate_momentum

logger = get_logger(__name__)

s = create_socket_connection()


def controller(momentum):
    """
    Network receiver controller that receives momentum commands via UDP.

    Args:
        momentum: Current momentum array [x, z, y, quit]

    Returns:
        Updated momentum array from network or current momentum if no data

    Raises:
        ControllerError: If network error persists
    """
    max_consecutive_errors = 10
    
    # Initialize error counter if not exists
    if not hasattr(controller, '_error_count'):
        controller._error_count = 0

    try:
        s.settimeout(0.00001)
        data, addr = s.recvfrom(1024)
        if data:
            if len(data) < 16:  # 4 floats * 4 bytes
                logger.warning(f"Received incomplete data from {addr}: {len(data)} bytes")
                return momentum

            momentum_new = np.frombuffer(data, dtype=np.float32)
            if len(momentum_new) < 4:
                logger.warning(f"Invalid momentum array length: {len(momentum_new)}")
                return momentum

            momentum = momentum_new[:4]  # Ensure exactly 4 elements
            
            # Validate momentum
            try:
                validate_momentum(momentum)
            except ValidationError as e:
                logger.warning(f"Invalid momentum received: {e}")
                return momentum
            
            controller._error_count = 0  # Reset error count on success
            logger.debug(f"Received momentum from {addr}: {momentum}")
    except socket.timeout:
        # Normal situation - no new data
        controller._error_count = 0
    except socket.error as e:
        controller._error_count += 1
        if controller._error_count >= max_consecutive_errors:
            logger.error(
                f"Network receiver failed {max_consecutive_errors} times consecutively: {e}",
                exc_info=True
            )
            raise ControllerError(
                f"Network receiver persistent failure: {e}"
            ) from e
        logger.warning(f"Network socket error (count: {controller._error_count}): {e}")
    except Exception as e:
        controller._error_count += 1
        logger.error(f"Network receiver error (count: {controller._error_count}): {e}", exc_info=True)
        if controller._error_count >= max_consecutive_errors:
            raise ControllerError(f"Network receiver failed: {e}") from e

    return momentum


if __name__ == "__main__":
    # Test network commands by logging momentum changes
    momentum = np.asarray([0, 0, 1, 0], dtype=np.float32)
    lm = momentum
    logger.info("Starting network receiver test")
    try:
        while True:
            momentum = controller(momentum)
            if (lm != momentum).any():
                logger.info(f"Momentum changed: {momentum}")
                lm = momentum
    except KeyboardInterrupt:
        logger.info("Network receiver test stopped")
