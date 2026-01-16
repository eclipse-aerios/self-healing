import subprocess
import asyncio

from utils.alerts_service import handle_alert
from config.loader import load_config

config = load_config()

SCENARIO = config.get("Communication_Monitoring", "scenario_name", fallback="Communication Failure Indication")
DEVICE_IP = config.get("Communication_Monitoring", "device_ip", fallback="10.0.0.238")
DEVICE_NAME = config.get("Communication_Monitoring", "device_name", fallback="Node")
CHECK_INTERVAL = config.getint("Communication_Monitoring", "check_interval", fallback=5)
PING_COUNT = config.getint("Communication_Monitoring", "ping_count", fallback=2)
PING_TIMEOUT = config.getint("Communication_Monitoring", "ping_timeout", fallback=1)

def healing_action():
    print(f"Communication failure detected for device {DEVICE_NAME}...")

def check_device_connectivity(ip_address: str, count=PING_COUNT, timeout=PING_TIMEOUT):
    command = ["ping", "-c", str(count), "-W", str(timeout), ip_address]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Failed to ping {ip_address}: {e}")
        return False
    
async def monitor_communication():
    """
    Periodically checks whether the device is able to communicate.
    """
    while True:
        is_connected = await asyncio.to_thread(check_device_connectivity, DEVICE_IP)
        
        if not is_connected:
            await handle_alert(scenario=SCENARIO, alert_msg=f"Communication failure detected for device {DEVICE_NAME} at {DEVICE_IP}.")
            healing_action()
        else:
            print(f"{DEVICE_NAME} is active and reachable.")
        await asyncio.sleep(60)
        
if __name__ == "__main__":
    monitor_communication()
