from fastapi import FastAPI
from api.monitor import router as monitor_router
app = FastAPI(
    title="AOIP Platform",
    description="Autonomous Multi-Agent Operational Intelligence Platform",
    version="1.0.0"
)
app.include_router(monitor_router)
@app.get("/")
def home():
    return {
        "message": "AOIP Backend Running Successfully"
    }
