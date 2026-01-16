import uvicorn
import datetime
import asyncio
import configparser

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

from alerts_service import fetch_alerts, add_alert, create_alert_object, send_alert_to_trust_manager

# Load Configuration
config = configparser.ConfigParser()
config.read("config.ini")

PORT = config.getint("api", "port", fallback=8500)

app = FastAPI()

class AlertRequest(BaseModel):
    timestamp: datetime.datetime
    scenario: str
    message: str

@app.post("/alerts", status_code=201)
async def create_alert(alert: AlertRequest):
    """Create a new alert."""
    try:
        alert_obj = create_alert_object(alert.scenario, alert.message)
        add_alert(alert_obj)
        asyncio.create_task(send_alert_to_trust_manager(alert_obj))
        return {"result": "Alert created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interal Server Error: {str(e)}")

@app.get("/alerts")
def get_alerts(since: str = Query(None, description=f"Fetch alerts after this timestamp (e.g. {datetime.datetime.now().date().isoformat()})")):
    """Get alerts since a given timestamp."""
    try:
        alerts = fetch_alerts(since)
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interal Server Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT) 