from pydantic import BaseModel


class AgentCreate(BaseModel):
	name: str
	type: str
	status: str


class StatusUpdate(BaseModel):
	status: str
