from fastapi import APIRouter
import psutil

router = APIRouter()

@router.get("/system-status")
def system_status():
    return {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent
    }
