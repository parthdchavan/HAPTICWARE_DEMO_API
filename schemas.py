from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    roll_no: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    roll_no: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = None

    class Config:
        from_attributes = True


class AgentCreate(BaseModel):
    name: str
    type: str
    status: str
    summary: Optional[str] = None

class AgentResponse(BaseModel):
    id: int
    name: str
    type: str
    status: str
    summary: Optional[str] = None

    class Config:
        from_attributes = True
