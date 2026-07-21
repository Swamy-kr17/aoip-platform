from fastapi import FastAPI

from api.health import router as health_router
from api.monitor import router as monitor_router
from api.task import router as task_router
from database.connection import engine
from database.base import Base
from models.agent import Agent
from models.task import Task
from api.agents import router as agents_router
from api.chat import router as chat_router
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AOIP Platform",
    description="Autonomous Multi-Agent Operational Intelligence Platform",
    version="1.0.0"
)

app.include_router(monitor_router)
app.include_router(health_router)
app.include_router(agents_router)
app.include_router(task_router)
app.include_router(chat_router)

@app.get("/")
def home():
    return {
        "message": "AOIP Backend Running Successfully"
    }