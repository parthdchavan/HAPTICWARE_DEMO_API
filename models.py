from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    roll_no = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=True)
    department = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', roll_no='{self.roll_no}', email='{self.email}')>"

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    summary = Column(String, nullable=True)

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}', status='{self.status}', summary='{self.summary}')>"
