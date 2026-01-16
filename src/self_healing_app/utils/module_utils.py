def is_running_on_rpi():
    """Check if the program is running on a Raspberry Pi."""
    try:
        with open("/proc/device-tree/model", "r") as f:
            model_info = f.read().lower()
            return "raspberry pi" in model_info
    except FileNotFoundError:
        return False
