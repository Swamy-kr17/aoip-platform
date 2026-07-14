from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str
    status: str
    agent_id: int


class TaskUpdate(BaseModel):
    title: str
    description: str
    status: str
    agent_id: int