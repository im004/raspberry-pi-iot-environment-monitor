#!/usr/bin/env python3
"""DHT temperature/humidity reader with retry handling.

The DHT11 can intermittently return checksum or timing errors. This module keeps
that behaviour contained in one place and returns clean `(humidity, temperature)`
values to the rest of the application.
"""
import logging
import os
import time
from typing import Optional, Tuple

import board
import adafruit_dht

from config import DHT_SENSOR_TYPE, DHT_MAX_FAIL_SECONDS, LOG_FILE

logger = logging.getLogger("ee3638.dht")
logger.setLevel(logging.INFO)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.propagate = False

if DHT_SENSOR_TYPE == "DHT11":
    DhtClass = adafruit_dht.DHT11
elif DHT_SENSOR_TYPE == "DHT22":
    DhtClass = adafruit_dht.DHT22
else:
    raise ValueError(f"Unsupported DHT_SENSOR_TYPE: {DHT_SENSOR_TYPE}")

# GPIO4/BCM maps to physical pin 7 on the Raspberry Pi header.
dht_device = DhtClass(board.D4)


def read_dht_once() -> Tuple[Optional[float], Optional[float]]:
    """Perform one DHT sensor read.

    Returns:
        (humidity_percent, temperature_c) when valid, otherwise (None, None).
    """
    try:
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity
        if humidity is None or temperature_c is None:
            return None, None
        return float(humidity), float(temperature_c)
    except RuntimeError as exc:
        # Typical DHT checksum/timing errors. A retry is expected.
        logger.warning("DHT RuntimeError: %s", exc)
        return None, None
    except Exception as exc:  # pragma: no cover - hardware-specific fallback
        logger.error("Unexpected DHT exception: %s", exc)
        return None, None


def read_dht_with_retries(
    max_fail_seconds: float = DHT_MAX_FAIL_SECONDS,
    delay: float = 2.0,
) -> Tuple[Optional[float], Optional[float]]:
    """Retry reads for up to `max_fail_seconds`.

    Returns the first valid `(humidity_percent, temperature_c)` pair, or
    `(None, None)` if no valid reading is obtained before the deadline.
    """
    deadline = time.monotonic() + max_fail_seconds
    attempt = 0

    while time.monotonic() < deadline:
        attempt += 1
        humidity, temperature_c = read_dht_once()
        if humidity is not None and temperature_c is not None:
            logger.info(
                "DHT read OK on attempt %d: %.1f%%, %.1f°C",
                attempt,
                humidity,
                temperature_c,
            )
            return humidity, temperature_c

        logger.warning("DHT read failed on attempt %d, retrying in %.1fs", attempt, delay)
        time.sleep(delay)

    logger.error("DHT read failed after %.1f seconds of retries", max_fail_seconds)
    return None, None


def main() -> None:
    humidity, temperature_c = read_dht_with_retries()
    if humidity is None or temperature_c is None:
        print("ERROR: Unable to get a valid reading from DHT sensor.")
    else:
        print(f"Humidity: {humidity:.1f}%  Temperature: {temperature_c:.1f}°C")


if __name__ == "__main__":
    main()
