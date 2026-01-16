import os
import datetime
import logging
import httpx

from config.loader import load_config

config = load_config()

LOCAL = config.getboolean("self_healing_api", "local", fallback=False)
if LOCAL:
    DOMAIN_URL = config.get("self_healing_api", "local_domain_url", fallback="self-healing-api")
else:
    DOMAIN_URL = config.get("self_healing_api", "domain_url", fallback="10.0.0.238")
DOMAIN_PORT = config.get("self_healing_api", "domain_port", fallback="8500")
REQUEST_TIMEOUT = config.getint("self_healing_api", "request_timeout", fallback=15)
ASYNC_REQUEST_TIMEOUT = config.getint("self_healing_api", "async_request_timeout", fallback=15)
MAC_ADDRESS = config.get("alerts", "mac_address", fallback="fa:16:3e:5e:25:ef")

class SelfHealingClient:
    def __init__(self):
        self.domain_url = DOMAIN_URL
        self.domain_port = DOMAIN_PORT

    def build_payload(self, scenario: str, message: str) -> dict:
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'scenario': scenario,
            'message': message
        }
    
    async def post_alert_async(self, scenario: str, message: str):
        url = f"http://{self.domain_url}:{self.domain_port}/alerts"
        print(f"Self-healing API endpoint URL: {url}")
        payload = self.build_payload(scenario, message)
        logging.info(f"Sending alert to Self-healing API: {payload}")

        async with httpx.AsyncClient(timeout=ASYNC_REQUEST_TIMEOUT) as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code in [200, 201]:
                    # logging.info(f"Alert added successfully to the Self-healing API")
                    print(f"[SUCCESS] Alert added successfully to the Self-healing API: {response.status_code}")
                else:
                    logging.error(f"Failed to add alert to the Self-healing API. The response status code is {response.status_code} and the message: {response.text}")
            except httpx.RequestError as e:
                logging.error(f"Failed to add alert to the the Self-healing API: {e}")
