import asyncio

from api_clients.self_healing_client import SelfHealingClient

async def handle_alert(scenario: str, alert_msg: str):
    """Handles the alert by storing it in log file and sending it to Self-healing API."""
    # add_alert(scenario, alert_msg)
    sh_client = SelfHealingClient()
    asyncio.create_task(sh_client.post_alert_async(scenario, alert_msg))
