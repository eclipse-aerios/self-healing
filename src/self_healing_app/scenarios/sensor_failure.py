import adafruit_dht
import board
import asyncio
import datetime

from utils.alerts_service import handle_alert
from utils.module_utils import is_running_on_rpi
from config.loader import load_config

config = load_config()

SCENARIO = config.get("Sensor_Monitoring", "scenario_name", fallback="Sensor Failure")
LOW_TEMPERATURE_THRESHOLD = config.getint("Sensor_Monitoring", "low_temperature_threshold", fallback=-20)
HIGH_TEMPERATURE_THRESHOLD = config.getint("Sensor_Monitoring", "high_temperature_threshold", fallback=60)
LOW_HUMIDITY_THRESHOLD = config.getint("Sensor_Monitoring", "low_humidity_threshold", fallback=10)
HIGH_HUMIDITY_THRESHOLD = config.getint("Sensor_Monitoring", "high_humidity_threshold", fallback=90)
SENSOR_POWER_PIN = config.getint("Sensor_Monitoring", "sensor_power_pin", fallback=90)
SENSOR_CHECK_MAX = config.getint("Sensor_Monitoring", "sensor_check_max", fallback=5)

def reset_sensor():
    if is_running_on_rpi():
        import RPi.GPIO as GPIO
        import time
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SENSOR_POWER_PIN, GPIO.OUT)
        GPIO.output(SENSOR_POWER_PIN, GPIO.LOW)
        time.sleep(2)
        GPIO.output(SENSOR_POWER_PIN, GPIO.HIGH)
        GPIO.cleanup()

def healing_action():
    if is_running_on_rpi():
        # reset_sensor()
        print("Resetting sensor...")
    else:
        print("Please exclude the sensor from monitoring.")

def check_outlier_values(humidity, temperature) -> bool:
    return (
        humidity is None or temperature is None or
        temperature <= LOW_TEMPERATURE_THRESHOLD or temperature >= HIGH_TEMPERATURE_THRESHOLD or
        humidity <= LOW_HUMIDITY_THRESHOLD or humidity >= HIGH_HUMIDITY_THRESHOLD
    )

def read_sensor_data(device) -> tuple:
    try:
        humidity, temperature = device.humidity, device.temperature
        return (humidity, temperature)
    except RuntimeError as e:
        return None, None

def init_sensor():
    try:    
        device = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    except AttributeError as e:
        device = None
    
    return device

async def monitor_sensor():
    """Monitors the sensor periodically, to detect threshold violations."""
    print(f"Monitoring sensors at {datetime.datetime.now()}...")
    while True:
        device = init_sensor()

        if device is None:
            print("Failed to initialize the sensor. Exiting sensor monitoring...")
            return
        
        for attempt in range(SENSOR_CHECK_MAX):
            humidity, temperature = read_sensor_data(device)
            
            if humidity is not None and temperature is not None:
                print(f"Sensor measurements are: Temperature {temperature}°C, Humidity {humidity}%")
                if check_outlier_values(humidity, temperature):
                    await handle_alert(scenario=SCENARIO, alert_msg= "Sensor measurement detected as an outlier.")
                    healing_action()

                break
            else:
                print("Failed to read sensor data. Retrying...")
                await asyncio.sleep(2)
        else:
            print("Failed to read sensor data after multiple attempts. Exclude sensor from monitoring...")
            healing_action()
    await asyncio.sleep(60)

if __name__ == "__main__":
    print("Starting sensor monitoring...")
    monitor_sensor()
