from fastapi import APIRouter

router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)

@router.get("/")
def get_agents():
    return {
        "message": "List of agents will appear here."
    }