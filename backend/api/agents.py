from fastapi import APIRouter
from sqlalchemy.orm import Session
from schemas.agent import AgentCreate, AgentUpdate
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

@router.put("/{agent_id}")
def update_agent(agent_id: int, agent: AgentUpdate):
    db: Session = SessionLocal()

    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not db_agent:
        db.close()
        return {"message": "Agent not found"}

    db_agent.name = agent.name
    db_agent.role = agent.role
    db_agent.status = agent.status

    db.commit()
    db.refresh(db_agent)

    db.close()

    return db_agent

@router.delete("/{agent_id}")
def delete_agent(agent_id: int):
    db: Session = SessionLocal()

    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not db_agent:
        db.close()
        return {"message": "Agent not found"}

    db.delete(db_agent)
    db.commit()

    db.close()

    return {"message": "Agent deleted successfully"}