#!/usr/bin/env python3
"""Flask dashboard and REST API for the Raspberry Pi IoT monitor."""
import csv
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

from config import DATA_DIR, HISTORY_LIMIT, PROJECT_ROOT, WEB_HOST, WEB_LOG_FILE, WEB_PORT
from gpio_control import cleanup as gpio_cleanup
from gpio_control import get_led_state, set_led, setup as gpio_setup

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "web" / "templates"),
    static_folder=str(PROJECT_ROOT / "web" / "static"),
)

gpio_setup()

logger = logging.getLogger("ee3638.web")
logger.setLevel(logging.INFO)
os.makedirs(os.path.dirname(WEB_LOG_FILE), exist_ok=True)
if not logger.handlers:
    handler = logging.FileHandler(WEB_LOG_FILE)
    formatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.propagate = False


def today_csv_path() -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    return os.path.join(DATA_DIR, f"readings_{date_str}.csv")


def get_latest_from_csv() -> Dict[str, Any]:
    """Return the latest row from today's CSV, or an empty dict if unavailable."""
    path = today_csv_path()
    if not os.path.exists(path):
        return {}

    last_row = None
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            last_row = row

    return last_row or {}


def get_history_from_csv(limit: int) -> List[Dict[str, Any]]:
    """Return the most recent `limit` rows from today's CSV."""
    path = today_csv_path()
    if not os.path.exists(path):
        return []

    with open(path, newline="") as file:
        rows = list(csv.DictReader(file))
    return rows[-limit:]


@app.route("/")
def dashboard():
    """Render the main dashboard page."""
    logger.info("GET /")
    return render_template("dashboard.html")


@app.route("/api/latest")
def api_latest():
    """Return the latest sensor reading from CSV storage."""
    logger.info("GET /api/latest")
    latest = get_latest_from_csv()
    if not latest:
        return jsonify({"status": "error", "source": "none", "data": None})

    data = {
        "timestamp_iso": latest["timestamp_iso"],
        "temperature_c": latest["temperature_c"],
        "humidity_percent": latest["humidity_percent"],
    }
    return jsonify({"status": "ok", "source": "csv", "data": data})


@app.route("/api/history")
def api_history():
    """Return recent sensor readings for the dashboard table/chart."""
    rows = get_history_from_csv(HISTORY_LIMIT)
    logger.info("GET /api/history, returning %d rows", len(rows))
    return jsonify({"count": len(rows), "data": rows})


@app.route("/api/led", methods=["GET"])
def api_led_status():
    """Return the current LED state."""
    return jsonify({"state": get_led_state()})


@app.route("/api/led", methods=["POST"])
def api_led_set():
    """Set LED state using JSON payload {"on": true|false}."""
    payload = request.get_json(silent=True) or {}
    turn_on = bool(payload.get("on", False))
    set_led(turn_on)
    return jsonify({"state": get_led_state()})


def main() -> None:
    try:
        app.run(host=WEB_HOST, port=WEB_PORT, debug=False)
    finally:
        gpio_cleanup()


if __name__ == "__main__":
    main()
