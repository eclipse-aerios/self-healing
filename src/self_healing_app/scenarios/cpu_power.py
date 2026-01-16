"""
Checks the CPU temperature periodically and detects any instances of
high temp. If high temp detected, appropriate action is taken.
"""

import subprocess
import asyncio
import datetime

from utils.alerts_service import handle_alert
from utils.module_utils import is_running_on_rpi
from config.loader import load_config

config = load_config()

LABEL_SELECTOR = "app=self-healing"
NAMESPACE = "default"

SCENARIO = config.get("CPU_Monitoring", "scenario_name", fallback="Device Power Alert")

HIG_THRESHOLD = config.getfloat("CPU_Monitoring", "high_threshold", fallback=85.0)
LOW_THRESHOLD = config.getfloat("CPU_Monitoring", "low_threshold", fallback=80.0)

HIGTHR_MSG = config.get("CPU_Messages", "high_alert", fallback="\033[0;31mHIGH THRESHOLD\033[0m")
LOWTHR_MSG = config.get("CPU_Messages", "low_alert", fallback="\033[0;33mLOW THRESHOLD\033[0m")
NORMAL_MSG = config.get("CPU_Messages", "normal", fallback="\033[0;32mNORMAL OPERATION\033[0m")

# def get_cpu_temp() -> float:
#     """Retrieve CPU temperature in Celsius, supporting both Raspberry Pi and general Linux systems."""
#     try:
#         temp = os.popen('vcgencmd measure_temp').readline().replace("temp=","").replace("'C\n","")
#         if temp:
#             return float(temp)
        
#         temps = psutil.sensors_temperatures()
#         if "coretemp" in temps:
#             return temps["coretemp"][0].current
#         elif "cpu_thermal" in temps:
#             return temps["cpu_thermal"][0].current
    
#     except Exception as e:
#         print(f"Error retrieving CPU temperature: {e}")
           
#     return None

def get_pod_name():
    """Finds the current running self-healing-app pod dynamically using `kubectl` shell command."""
    try:
        command = f"kubectl get pods -n {NAMESPACE} -l {LABEL_SELECTOR} --no-headers -o custom-columns=:metadata.name"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        pod_name = result.stdout.strip().split("\n")[0]  # Get the first pod name
        return pod_name if pod_name else None
    except subprocess.CalledProcessError:
        print("Failed to get pod name")
        return None

def restart_pod():
    """Deletes the pod using `kubectl delete pod`, allowing Kubernetes to restart it."""
    pod_name = get_pod_name()
    if not pod_name:
        print("No running pod found to restart.")
        return

    print(f"Restarting pod: {pod_name}")
    subprocess.run(f"kubectl delete pod {pod_name} -n {NAMESPACE}", shell=True)

def healing_action(cpu_usage, msg):
    """Takes the healing action for the detected anomaly."""
    if cpu_usage > HIG_THRESHOLD:
        print(f"CPU power is too high at {cpu_usage} 'C. Taking healing action...")
        if is_running_on_rpi():
            print("Restarting the Raspberry Pi...")
            # subprocess.run(["sudo", "reboot"])
        else:
            pod_name = get_pod_name()
            print(f"Restarting the self-healing-app pod: {pod_name} ...")
            # restart_pod()

def status_report(cpu_usage):
    """Reports the status of CPU power."""
    status = NORMAL_MSG
    if cpu_usage >= HIG_THRESHOLD:
        status = HIGTHR_MSG
    elif cpu_usage >= LOW_THRESHOLD:
        status = LOWTHR_MSG
    return status

def detect_anomaly(cpu_usage: float):
    """Detects anomalies in CPU temperature and usage."""
    if cpu_usage is not None and status_report(cpu_usage) != NORMAL_MSG:
        return f"Exceeded threshold: {cpu_usage}%"
    
    return None

def get_cpu_usage() -> float:
    """Returns the CPU usage percentage using the 'top' command."""
    try:
        output = subprocess.check_output("""top -bn1 | grep "Cpu(s)" | awk -F ',' '{print 100 - $4}' | awk '{print $1}'""", shell=True, text=True)
        return float(output.strip())  # Convert to float
    except Exception as e:
        print(f"Error retrieving CPU usage: {e}")
        return None

async def monitor_cpu_power():
    """Monitors CPU periodically, to detect threshold violations."""
    while True:
        print(f"Monitoring CPU power at {datetime.datetime.now()}...")
        cpu_usage = get_cpu_usage()
        anomaly = detect_anomaly(cpu_usage)
        if anomaly:
            await handle_alert(scenario=SCENARIO, alert_msg= anomaly)
            healing_action(cpu_usage, anomaly)
        else:
            await handle_alert(scenario=SCENARIO, alert_msg= "Test connection between services")
            print(f"CPU Power: {cpu_usage}%")
        await asyncio.sleep(60)

if __name__ == "__main__":
    monitor_cpu_power()