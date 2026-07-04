#!/usr/bin/env python3
"""CSV data logger for DHT11 temperature/humidity readings."""
import csv
import logging
import os
import time
from datetime import datetime

from config import DATA_DIR, LOG_FILE, READ_INTERVAL_SECONDS
from dht_reader import read_dht_with_retries

logger = logging.getLogger("ee3638.logger")
logger.setLevel(logging.INFO)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.propagate = False


def current_csv_path() -> str:
    """Return the CSV path for today's readings."""
    date_str = datetime.now().strftime("%Y%m%d")
    return os.path.join(DATA_DIR, f"readings_{date_str}.csv")


def ensure_csv_header(path: str) -> None:
    """Create a CSV file with header row if it does not exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp_iso", "temperature_c", "humidity_percent"])
        logger.info("Created new CSV log file: %s", path)


def append_reading(path: str, timestamp_iso: str, temperature_c: float, humidity: float) -> None:
    """Append one validated sensor reading to the CSV file."""
    with open(path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp_iso, f"{temperature_c:.1f}", f"{humidity:.1f}"])


def main() -> None:
    logger.info("Starting data logger loop, interval = %ds", READ_INTERVAL_SECONDS)

    while True:
        csv_path = current_csv_path()
        ensure_csv_header(csv_path)

        timestamp_iso = datetime.now().isoformat(timespec="seconds")
        humidity, temperature_c = read_dht_with_retries()

        if humidity is None or temperature_c is None:
            logger.warning("Skipping write: no valid DHT reading at %s", timestamp_iso)
        else:
            append_reading(csv_path, timestamp_iso, temperature_c, humidity)
            logger.info(
                "Logged reading at %s: %.1f°C, %.1f%%",
                timestamp_iso,
                temperature_c,
                humidity,
            )
            print(f"{timestamp_iso}  {temperature_c:.1f}°C  {humidity:.1f}%")

        time.sleep(READ_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
