from fastapi import FastAPI

app = FastAPI(
    title="AOIP Platform",
    description="Autonomous Multi-Agent Operational Intelligence Platform",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "AOIP Backend Running Successfully"
    }
