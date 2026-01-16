import datetime
import logging
import httpx

from config.loader import load_config

config = load_config()

DOMAIN_URL = config.get("TrustManager", "domain_url", fallback="10.254.102.73")
DOMAIN_PORT = config.get("TrustManager", "domain_port", fallback="3000")
REQUEST_TIMEOUT = config.getint("TrustManager", "request_timeout", fallback=15)
ASYNC_REQUEST_TIMEOUT = config.getint("TrustManager", "async_request_timeout", fallback=15)
MAC_ADDRESS = config.get("Alerts", "mac_address", fallback="fa:16:3e:5e:25:ef")

class TrustManagerClient:
    def __init__(self):
        self.domain_url = DOMAIN_URL
        self.domain_port = DOMAIN_PORT

    def get_mac_address(self) -> str:
        return MAC_ADDRESS  
        # mac = uuid.getnode()  # Get MAC as integer
        # mac_hex = ':'.join(f'{(mac >> i) & 0xFF:02x}' for i in range(0, 48, 8)[::-1])
        # return mac_hex

    def build_payload(self, scenario: str, message: str) -> dict:
        mac_address = self.get_mac_address()
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'scenario': scenario,
            'message': message,
            'mac_address': mac_address
        }
    
    async def post_alert_async(self, scenario: str, message: str):
        url = f"http://{self.domain_url}:{self.domain_port}/health"
        payload = self.build_payload(scenario, message)
        logging.info(f"Sending alert to TrustManager: {payload}")

        async with httpx.AsyncClient(timeout=ASYNC_REQUEST_TIMEOUT) as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code in [200, 201]:
                    logging.info(f"Alert added successfully to the Trust Manager component")
                else:
                    logging.error(f"Failed to add alert to the Trust Manager component")
            except httpx.RequestError as e:
                logging.error(f"Failed to add alert to the Trust Manager component: {e}")