import os
import json
import datetime
import configparser
from getmac import get_mac_address

from trust_manager_client import TrustManagerClient

# Load Configuration
config = configparser.ConfigParser()
config.read("config.ini")

ALERTS_FILE = config.get("log_file", "name", fallback="alerts.json")
MAX_ALERTS = config.getint("log_file", "max_records", fallback=250)
MAC_ADDRESS = "fa:16:3e:5e:25:ef"

FILE_PATH = os.path.join(os.path.dirname(__file__), ALERTS_FILE)

def fetch_mac_address():
    """Get the MAC address of the device."""
    mac_address = get_mac_address()
    if mac_address:
        return mac_address
    return MAC_ADDRESS

def save_alerts(alerts):
    """Save alerts to the JSON file, keeping the latest MAX_ALERTS."""
    alerts = alerts[-MAX_ALERTS:]  # Keep only the last MAX_ALERTS
    with open(FILE_PATH, "w") as file:
        json.dump(alerts, file, indent=4)

def load_alerts():
    """Load alerts from the JSON file."""
    print(FILE_PATH)
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def add_alert(alert: dict):
    """Add a new alert and save it to the file."""
    alerts = load_alerts()
    alerts.append(alert)
    save_alerts(alerts)

def fetch_alerts(since_timestamp=None):
    """Retrieve alerts, optionally filtering by timestamp."""
    alerts = load_alerts()
    if since_timestamp:
        return [a for a in alerts if a["timestamp"] > since_timestamp]
    return alerts

def create_alert_object(scenario, message):
    """Create an alert object."""
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "scenario": scenario,
        "message": message,
        "mac_address": fetch_mac_address()
    }

async def send_alert_to_trust_manager(alert: dict):
    """Send alert to the Trust Manager component."""
    tm_client = TrustManagerClient()
    await tm_client.post_alert_async(alert)