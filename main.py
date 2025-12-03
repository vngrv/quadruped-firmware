#!/usr/bin/env python3
"""Main entry point for quadruped robot control application.

This is the standard entry point for the quadruped robot firmware.
It provides a clean interface to start the robot control system.

Usage:
    python3 main.py
    python3 main.py --controller src.controllers.local_keyboard_controller
    python3 main.py --config src/config/robot_config.yaml --log-level DEBUG
"""

from src.control_quadruped import main
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import main function from source module

if __name__ == "__main__":
    main()
