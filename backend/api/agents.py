from fastapi import APIRouter
from sqlalchemy.orm import Session
from schemas.agent import AgentCreate
from database.connection import SessionLocal
from models.agent import Agent

router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)


@router.get("/")
def get_agents():
    db: Session = SessionLocal()

    agents = db.query(Agent).all()

    db.close()

    return agents


@router.post("/")
def create_agent(agent: AgentCreate):
    db: Session = SessionLocal()

    new_agent = Agent(
        name=agent.name,
        role=agent.role,
        status=agent.status
    )

    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    db.close()

    return new_agent