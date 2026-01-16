import subprocess
import time
import re
import asyncio
import configparser

from utils.alerts_service import handle_alert
from config.loader import load_config

config = load_config()

SCENARIO = config.get("Network_Protocol", "scenario_name", fallback="Network Protocol Violation")
# INTERFACE = config.get("Network_Protocol", "interface", fallback="wlan0")
DC_LIMIT = config.getfloat("Network_Protocol", "dc_limit", fallback=0.001)
CYCLE_PERIOD = config.getint("Network_Protocol", "cycle_period", fallback=30)
AVG_PACKET_SIZE = config.getint("Network_Protocol", "avg_packet_size", fallback=1500)
MAX_TRANSMIT_TIME = CYCLE_PERIOD * DC_LIMIT  # Calculate maximum allowed transmission time

# **Duty Cycle Tracking Variables**
transmit_duration = 0  # Stores cumulative active transmission time
cycle_start_time = time.time()  # Tracks start time of duty cycle measurement

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
print(f"Using Network Interface: {INTERFACE}")

def healing_action():
    print("Executing healing action: Reconfiguring transmission parameters.")
    #subprocess.run(['iwconfig', INTERFACE, 'txpower', '10'], check=True)

def get_transmitted_packets(interface):
    """Fetches the number of packets transmitted by the network interface using ifconfig."""
    try:
        output = subprocess.check_output(['ifconfig', interface], text=True)
        packets = re.search(r'TX packets (\d+)', output)
        if packets:
            return int(packets.group(1))
    except subprocess.CalledProcessError as e:
        print(f"Failed to get transmitted packets: {e}")
    return 0  # Return 0 if unable to fetch data

async def calculate_active_time(interface, transmission_speed, interval=1.0):
    """Calculates estimated active transmission time over a given interval."""
    start_packets = get_transmitted_packets(interface)
    await asyncio.sleep(interval)  # Wait for the interval
    end_packets = get_transmitted_packets(interface)
    
    packets_sent = end_packets - start_packets
    
    if packets_sent < 0:
        packets_sent = 0

    # Calculate active transmission time based on packets sent
    active_time = (packets_sent * AVG_PACKET_SIZE) / transmission_speed
    return active_time

def reset_cycle():
    """Resets the Duty Cycle counter."""
    global transmit_duration, cycle_start_time
    print("Resetting Duty Cycle counter.")
    transmit_duration = 0  # Reset transmit duration 
    cycle_start_time = time.time()  # Reset start time

def get_transmission_speed(interface):
    """Fetches the current transmission speed (bit rate) in bytes per second using iwconfig."""
    try:
        output = subprocess.check_output(['iwconfig', interface], text=True)
        bitrate = re.search(r'Bit Rate=(\d+\.?\d*) Mb/s', output)
        if bitrate:
            speed_mbps = float(bitrate.group(1))
            transmission_speed = (speed_mbps * 1e6) / 8  # Convert Mbps to bytes per second
            return transmission_speed
    except subprocess.CalledProcessError as e:
        print(f"Failed to get transmission speed: {e}")
    return (1 * 1e6) / 8  # Default to 1 Mbps in bytes per second if unable to fetch

async def check_dc_violation():
    """Checks if Duty Cycle is within limits and triggers healing action if exceeded."""
    global transmit_duration, cycle_start_time

    # Retrieve the transmission speed dynamically
    transmission_speed = get_transmission_speed(INTERFACE)
    
    current_time = time.time()
    elapsed_time = current_time - cycle_start_time

    # Reset the Duty Cycle counter if the cycle period has elapsed
    if elapsed_time >= CYCLE_PERIOD:
        reset_cycle()
        transmission_speed = get_transmission_speed(INTERFACE) # Update transmission speed

    # Check if within Duty Cycle limit
    if transmit_duration < MAX_TRANSMIT_TIME:
        # Calculate active transmission time and accumulate it
        active_time = await calculate_active_time(INTERFACE, transmission_speed)
        transmit_duration += active_time
        print(f"Duty Cycle is within limits: {transmit_duration:.2f} %")
    else:
        print("Duty Cycle limit reached. Executing healing action.")
        await handle_alert(scenario=SCENARIO, alert_msg= 'Duty Cycle violation detected. Reconfiguring transmission parameters.')
        healing_action()
        reset_cycle()

async def enable_monitoring_agent():
    """Main function to enable the monitoring agent and check for Duty Cycle violations."""
    print("Monitoring agent started. Checking for Duty Cycle violations...")
    while True:
        await check_dc_violation()
        await asyncio.sleep(60)
        
# Run the Duty Cycle monitoring
if __name__ == "__main__":
    enable_monitoring_agent()
