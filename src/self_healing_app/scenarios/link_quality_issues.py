import re
import time
import serial
import asyncio
import subprocess

from utils.alerts_service import handle_alert
from config.loader import load_config

config = load_config()

SCENARIO = config.get("Link_Quality", "scenario_name", fallback="Link Quality Issues")
# INTERFACE = config.get("Link_Quality", "interface", fallback="wlan0")
SERIAL_PORT = config.get("Link_Quality", "serial_port", fallback="/dev/ttyS0")
BAUD_RATE = config.getint("Link_Quality", "baud_rate", fallback=9600)
COMM_TYPE = config.get("Link_Quality", "communication_type", fallback="wifi")
CHECK_INTERVAL = config.getint("Link_Quality", "check_interval", fallback=5)
HISTORY_SIZE = config.getint("Link_Quality", "history_size", fallback=10)
RSSI_MARGIN = config.getint("Link_Quality", "rssi_margin", fallback=5)
LINK_QUALITY_MARGIN = config.getint("Link_Quality", "link_quality_margin", fallback=10)
SNR_MARGIN = config.getint("Link_Quality", "snr_margin", fallback=3)
HEALING_COOLDOWN = config.getint("Link_Quality", "healing_cooldown", fallback=30)

last_healing_time = 0
rssi_history_data = []
link_quality_history_data = []
snr_history_data = []
sf_history_data = []

def get_primary_network_interface():
    """Finds the primary network interface dynamically."""
    try:
        output = subprocess.check_output(['ip', 'route'], text=True)
        match = re.search(r'default via .* dev (\S+)', output)
        if match:
            return match.group(1)  # Extracts interface name
    except Exception as e:
        print(f"Error detecting network interface: {e}")
    return "eth0"  # Default to eth0 if detection fails

# Dynamically detect network interface
INTERFACE = get_primary_network_interface()

def healing_action():
    """Reports a link quality issue and applies a healing action to reconfigure link parameters."""
    global last_healing_time
    current_time = time.time()
    if current_time - last_healing_time < HEALING_COOLDOWN:
        return

    print("Executing healing action: Reconfiguring transmission parameters.")
    last_healing_time = current_time

def store_radio_values(rssi, link_quality=None, snr=None, sf=None):
    """Stores the radio values in the memory, maintaining history size limits."""
    if rssi is not None:
        rssi_history_data.append(rssi)
        if len(rssi_history_data) > HISTORY_SIZE:
            rssi_history_data.pop(0)
    if COMM_TYPE == "wifi" and link_quality is not None:
        link_quality_history_data.append(link_quality)
        if len(link_quality_history_data) > HISTORY_SIZE:
            link_quality_history_data.pop(0)
    if COMM_TYPE == "lora":
        if snr is not None:
            snr_history_data.append(snr)
            if len(snr_history_data) > HISTORY_SIZE:
                snr_history_data.pop(0)
        if sf is not None:
            sf_history_data.append(sf)
            if len(sf_history_data) > HISTORY_SIZE:
                sf_history_data.pop(0)

def set_threshold_based_on_past_values(history, margin):
    """Sets a dynamic threshold based on past values."""
    if len(history) == 0:
        return None
    avg_value = sum(history) / len(history)
    return avg_value - margin

def extract_spreading_factor(packet):
    """Extracts spreading factor (SF) from LoRa packet."""
    match = re.search(r'SF: (\d+)', packet)
    return int(match.group(1)) if match else None

def extract_snr(packet):
    """Extracts SNR value from LoRa packet."""
    match = re.search(r'SNR: (-?\d+\.\d+) dB', packet)
    return float(match.group(1)) if match else None

def extract_rssi(packet):
    """Extracts RSSI value from LoRa packet."""
    match = re.search(r'RSSI: (-?\d+) dBm', packet)
    return int(match.group(1)) if match else None

def get_lora_radio_values():
    """Retrieves radio values (RSSI, SNR, SF) for LoRa."""
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            if ser.in_waiting > 0:
                packet = ser.readline().decode('utf-8').strip()
                print(f"Received LoRa Packet: {packet}")
                rssi = extract_rssi(packet)
                snr = extract_snr(packet)
                sf = extract_spreading_factor(packet)
                print(f"RSSI: {rssi} dBm, SNR: {snr} dB, SF: {sf}")
                return rssi, snr, sf
    except Exception as e:
        print(f"Error retrieving LoRa values: {e}")
    return None, None, None

def get_wifi_radio_values(interface):
    """Retrieves radio values (RSSI and Link Quality) for the given interface."""
    try:
        output = subprocess.check_output(['iwconfig', interface], text=True)
        rssi_line = re.search(r'Signal level=(-\d+)', output)
        rssi = int(rssi_line.group(1)) if rssi_line else None
        link_quality_line = re.search(r'Link Quality=(\d+)/(\d+)', output)
        if link_quality_line:
            link_quality = int(link_quality_line.group(1))
            max_quality = int(link_quality_line.group(2))
            link_quality_percent = round((link_quality / max_quality) * 100, 2)
            return rssi, link_quality_percent
        else:
            print("Warning: Link Quality not found in iwconfig output.")
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving values: {e}")
    return None, None

def check_radio_values():
    """Checks if current radio values are below the dynamic threshold and triggers a healing action if needed."""
    if COMM_TYPE == "wifi":
        rssi, link_quality = get_wifi_radio_values(INTERFACE)
        radio_values = {
            "rssi": rssi,
            "link_quality": link_quality,
            "snr": None,
            "sf": None
        }
    elif COMM_TYPE == "lora":
        radio_values = {
            "rssi": get_lora_radio_values()[0],
            "snr": get_lora_radio_values()[1],
            "sf": get_lora_radio_values()[2],
            "link_quality": None
        }

    store_radio_values(
        radio_values["rssi"], 
        radio_values["link_quality"],
        radio_values["snr"], 
        radio_values["sf"]
    )

    thresholds = {
        "rssi": set_threshold_based_on_past_values(rssi_history_data, RSSI_MARGIN),
        "link_quality": set_threshold_based_on_past_values(link_quality_history_data, LINK_QUALITY_MARGIN) if COMM_TYPE == "wifi" else None,
        "snr": set_threshold_based_on_past_values(snr_history_data, SNR_MARGIN) if COMM_TYPE == "lora" else None
    }

    for key, value in radio_values.items():
        threshold = thresholds.get(key)
        if value is not None and threshold is not None and value < threshold:
            handle_alert(scenario=SCENARIO, alert_msg=f"Link quality issue detected. Adjusting transmission parameters.")
            healing_action()
        else:
            print(f"No link quality issue detected for {key} with value {value}.") if value is not None else ""

async def check_radio_values_async():
    """Async wrapper for checking radio values without blocking."""
    await asyncio.to_thread(check_radio_values)

async def monitor_link_quality():
    """Main loop for monitoring link quality."""
    while True:
        await check_radio_values_async()
        await asyncio.sleep(60)
        
if __name__ == "__main__":
    monitor_link_quality()
