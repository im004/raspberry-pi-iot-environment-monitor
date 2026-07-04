"""Central configuration for the EE3638 Raspberry Pi IoT monitor."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Sensor configuration
DHT_SENSOR_TYPE = "DHT11"
DHT_GPIO_PIN = 4  # BCM GPIO4, physical pin 7

# LED actuator configuration
LED_GPIO_PIN = 17  # BCM GPIO17, physical pin 11
LED_ACTIVE_HIGH = True

# Timing configuration
READ_INTERVAL_SECONDS = 5
MAX_READ_RETRIES = 5
RETRY_DELAY_SECONDS = 2
DHT_MAX_FAIL_SECONDS = 10

# Runtime folders
DATA_DIR = str(PROJECT_ROOT / "data")
LOG_DIR = str(PROJECT_ROOT / "logs")
LOG_FILE = str(PROJECT_ROOT / "logs" / "app.log")
WEB_LOG_FILE = str(PROJECT_ROOT / "logs" / "web.log")

# Dashboard/API behaviour
HISTORY_LIMIT = 50
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
