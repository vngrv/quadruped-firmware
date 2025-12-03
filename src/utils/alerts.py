"""Alert system for critical errors."""

import time
from typing import Optional, List
from src.utils.logger import get_logger
from src.utils.exceptions import QuadrupedError

logger = get_logger(__name__)


class AlertSystem:
    """System for alerting on critical errors."""

    def __init__(self):
        """Initialize alert system."""
        self.alert_history: List[dict] = []
        self.max_history = 100

    def send_alert(
        self,
        level: str,
        message: str,
        exception: Optional[Exception] = None
    ) -> None:
        """
        Send alert for critical error.

        Args:
            level: Alert level ('critical', 'warning', 'error')
            message: Alert message
            exception: Optional exception that caused the alert
        """
        alert = {
            'level': level,
            'message': message,
            'exception': str(exception) if exception else None,
            'timestamp': time.time()
        }

        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)

        # Log alert
        if level == 'critical':
            logger.critical(f"CRITICAL ALERT: {message}")
            if exception:
                logger.critical(f"Exception: {exception}", exc_info=True)
        elif level == 'error':
            logger.error(f"ERROR ALERT: {message}")
            if exception:
                logger.error(f"Exception: {exception}", exc_info=True)
        else:
            logger.warning(f"WARNING ALERT: {message}")

    def get_recent_alerts(self, limit: int = 10) -> List[dict]:
        """
        Get recent alerts.

        Args:
            limit: Maximum number of alerts to return

        Returns:
            List of recent alerts
        """
        return self.alert_history[-limit:]

    def clear_history(self) -> None:
        """Clear alert history."""
        self.alert_history.clear()


# Global alert system instance
_alert_system = AlertSystem()


def send_critical_alert(message: str, exception: Optional[Exception] = None) -> None:
    """
    Send critical alert.

    Args:
        message: Alert message
        exception: Optional exception
    """
    _alert_system.send_alert('critical', message, exception)


def send_error_alert(message: str, exception: Optional[Exception] = None) -> None:
    """
    Send error alert.

    Args:
        message: Alert message
        exception: Optional exception
    """
    _alert_system.send_alert('error', message, exception)


def send_warning_alert(message: str) -> None:
    """
    Send warning alert.

    Args:
        message: Alert message
    """
    _alert_system.send_alert('warning', message)


def get_recent_alerts(limit: int = 10) -> List[dict]:
    """
    Get recent alerts.

    Args:
        limit: Maximum number of alerts

    Returns:
        List of recent alerts
    """
    return _alert_system.get_recent_alerts(limit)

