"""GPIO LED control abstraction.

The real Raspberry Pi deployment uses an LED on BCM GPIO17 through a current-limiting
resistor. A no-op fallback is included so the Flask app can still be imported on a
non-Raspberry Pi machine for code review or UI development.
"""
import logging
from typing import Optional

from config import LED_ACTIVE_HIGH, LED_GPIO_PIN

logger = logging.getLogger("ee3638.gpio")

try:  # pragma: no cover - depends on Raspberry Pi hardware
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):  # pragma: no cover - development fallback
    GPIO = None  # type: ignore[assignment]
    GPIO_AVAILABLE = False

_led_state = False


def setup() -> None:
    """Initialise the LED GPIO pin."""
    if not GPIO_AVAILABLE:
        logger.warning("RPi.GPIO not available; GPIO control running in no-op mode")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_GPIO_PIN, GPIO.OUT)
    set_led(False)


def set_led(on: bool) -> None:
    """Set the LED state."""
    global _led_state
    _led_state = bool(on)

    if not GPIO_AVAILABLE:
        logger.info("Simulated LED state set to %s", _led_state)
        return

    output_value = GPIO.HIGH if (_led_state == LED_ACTIVE_HIGH) else GPIO.LOW
    GPIO.output(LED_GPIO_PIN, output_value)


def get_led_state() -> bool:
    """Return the last requested LED state."""
    return _led_state


def cleanup() -> None:
    """Reset GPIO resources on shutdown."""
    if GPIO_AVAILABLE:
        set_led(False)
        GPIO.cleanup(LED_GPIO_PIN)
