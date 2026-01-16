import datetime
import logging
import httpx
import uuid
import configparser

# Load Configuration
config = configparser.ConfigParser()
config.read("config.ini")

DOMAIN_URL = config.get("trust_manager", "domain_url", fallback="10.254.102.73")
DOMAIN_PORT = config.get("trust_manager", "domain_port", fallback="3000")
REQUEST_TIMEOUT = config.getint("trust_manager", "request_timeout", fallback=15)
ASYNC_REQUEST_TIMEOUT = config.getint("trust_manager", "async_request_timeout", fallback=15)

class TrustManagerClient:
    def __init__(self):
        self.domain_url = DOMAIN_URL
        self.domain_port = DOMAIN_PORT

    async def post_alert_async(self, alert: dict):
        url = f"http://{self.domain_url}:{self.domain_port}/health"
        print(f"Sending alert to Trust Manager: {url} component: {alert}")
        async with httpx.AsyncClient(timeout=ASYNC_REQUEST_TIMEOUT) as client:
            try:
                response = await client.post(url, json=alert)
                if response.status_code in [200, 201]:
                    logging.info(f"Alert added successfully to the Trust Manager component")
                else:
                    logging.error(f"Failed to add alert to the Trust Manager component")
            except httpx.RequestError as e:
                logging.error(f"Failed to add alert to the Trust Manager component: {e}")
