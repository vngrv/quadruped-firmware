"""Configuration loader for quadruped robot firmware."""

import yaml
from pathlib import Path
from typing import Dict, Any
from src.utils.exceptions import ConfigError
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_config(config_file: Path) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_file: Path to YAML configuration file

    Returns:
        Dictionary with configuration values

    Raises:
        ConfigError: If configuration file cannot be loaded
    """
    try:
        if not config_file.exists():
            raise ConfigError(f"Configuration file not found: {config_file}")

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        if config is None:
            raise ConfigError(f"Configuration file is empty: {config_file}")

        logger.info(f"Loaded configuration from {config_file}")
        return config

    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in configuration file: {e}") from e
    except Exception as e:
        raise ConfigError(f"Failed to load configuration: {e}") from e


def get_config_path(config_name: str) -> Path:
    """
    Get path to configuration file.

    Args:
        config_name: Name of configuration file (without .yaml extension)

    Returns:
        Path to configuration file
    """
    config_dir = Path(__file__).parent
    return config_dir / f"{config_name}.yaml"

