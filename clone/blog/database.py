# database.py
# ─────────────────────────────────────────────────────
# This file handles everything related to the DATABASE
# It creates the connection, session, and base class
# ─────────────────────────────────────────────────────

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# This line connects to a SQLite file called blog.db
# check_same_thread=False is required for SQLite + FastAPI
engine = create_engine("sqlite:///./blog.db", connect_args={"check_same_thread": False})

# SessionLocal is like a "conversation" with the database
# Every request gets its own session to read/write data
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class that all our table models will inherit from
class Base(DeclarativeBase):
    pass

# ─────────────────────────────────────────────────────
# get_db() is a dependency used in every route
# It opens a DB session before the request
# and closes it after the request is done
# ─────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db       # hands the session to the route function
    finally:
        db.close()     # always close to free up resources
