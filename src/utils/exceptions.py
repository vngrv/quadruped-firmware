"""Custom exceptions for the quadruped robot firmware."""


class QuadrupedError(Exception):
    """Base exception for all quadruped robot errors."""
    pass


class ServoError(QuadrupedError):
    """Exception raised for servo motor errors."""
    pass


class KinematicsError(QuadrupedError):
    """Exception raised for inverse kinematics calculation errors."""
    pass


class ControllerError(QuadrupedError):
    """Exception raised for controller errors."""
    pass


class ConfigError(QuadrupedError):
    """Exception raised for configuration errors."""
    pass


class ValidationError(QuadrupedError):
    """Exception raised for input validation errors."""
    pass

