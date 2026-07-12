from pydantic import BaseModel


class AgentCreate(BaseModel):
    name: str
    role: str
    status: str

class AgentUpdate(BaseModel):
    name: str
    role: str
    status: str