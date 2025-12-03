"""Network utilities for socket connections."""

import socket
from src.utils.logger import get_logger
from src.utils.exceptions import ConfigError

logger = get_logger(__name__)


def get_ip() -> str:
    """
    Get the local IP address of this machine.

    Returns:
        IP address as string, defaults to '127.0.0.1' if detection fails
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        logger.debug(f"Detected local IP: {ip}")
    except Exception as e:
        logger.warning(f"Failed to detect IP address: {e}, using localhost")
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def create_socket_connection(start_port: int = 5000, max_port: int = 9999):
    """
    Create a UDP socket connection on an available port.

    Args:
        start_port: Starting port number to try
        max_port: Maximum port number to try

    Returns:
        Bound UDP socket

    Raises:
        ConfigError: If no available port is found
    """
    host = get_ip()
    port = start_port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    max_attempts = min(start_port + 1000, max_port)

    while port < max_attempts:
        try:
            s.bind((host, port))
            logger.info(f"Socket bound - IP: {host}, Port: {port}")
            return s
        except OSError as e:
            logger.debug(f"Port {port} unavailable, trying next")
            port += 1

    s.close()
    raise ConfigError(
        f"No available port found in range [{start_port}, {max_attempts}]"
    )
