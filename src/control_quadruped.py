"""Main entry point for quadruped robot control."""

import importlib
import argparse
import sys
from pathlib import Path

from src.robot.quadruped import Quadruped
from src.config.config_loader import load_config, get_config_path
from src.utils.logger import setup_logger, get_logger
from src.utils.exceptions import ConfigError, ControllerError, ServoError

# Setup logging with file rotation
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)
logger = setup_logger('quadruped', log_file=log_dir / 'quadruped.log')


def get_controller(controller_file: str):
    """
    Dynamically load a controller module.

    Args:
        controller_file: Module path to controller (e.g., 'controllers.network_receiver')

    Returns:
        Controller function

    Raises:
        ControllerError: If controller cannot be loaded
    """
    try:
        logger.info(f"Loading controller: {controller_file}")
        controller_lib = importlib.import_module(controller_file)
        if not hasattr(controller_lib, 'controller'):
            raise ControllerError(f"Controller module {controller_file} has no 'controller' function")
        return controller_lib.controller
    except ImportError as e:
        logger.error(f"Failed to import controller {controller_file}: {e}")
        raise ControllerError(f"Controller {controller_file} not found") from e
    except Exception as e:
        logger.error(f"Error loading controller: {e}", exc_info=True)
        raise ControllerError(f"Failed to load controller: {e}") from e


def main():
    """Main entry point for the quadruped robot control."""
    parser = argparse.ArgumentParser(
        description='Quadruped Robot Control System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--controller',
        default='src.controllers.network_receiver',
        help='Controller module path (default: controllers.network_receiver)'
    )
    parser.add_argument(
        '--config',
        type=str,
            help='Path to robot configuration file (default: src/config/robot_config.yaml)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Set logging level
    import logging
    logger.setLevel(getattr(logging, args.log_level))

    try:
        # Load configuration
        if args.config:
            config_path = Path(args.config)
        else:
            config_path = get_config_path('robot_config')

        logger.info(f"Loading configuration from {config_path}")
        config = load_config(config_path)

        # Load controller
        controller = get_controller(args.controller)

        # Initialize robot
        logger.info("Initializing quadruped robot")
        robot = Quadruped(config)

        # Calibrate robot
        logger.info("Calibrating robot")
        if not robot.calibrate():
            logger.error("Robot calibration failed")
            sys.exit(1)

        # Start movement
        logger.info("Starting robot movement")
        robot.move(controller)

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(0)
    except (ConfigError, ControllerError, ServoError) as e:
        logger.error(f"Configuration or initialization error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
