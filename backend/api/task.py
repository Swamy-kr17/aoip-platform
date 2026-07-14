from fastapi import APIRouter
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.get("/")
def get_tasks():
    db: Session = SessionLocal()

    tasks = db.query(Task).all()

    db.close()

    return tasks


@router.post("/")
def create_task(task: TaskCreate):
    db: Session = SessionLocal()

    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        agent_id=task.agent_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    db.close()

    return new_task