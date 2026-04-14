from fastapi import FastAPI
from database import engine, Base
from sqlalchemy import text
import models
from routes.agent_routes import router as agent_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Ensure old databases also get the summary column.
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS summary VARCHAR"))

app.include_router(agent_router)

@app.get("/")
def home():
    return {"message": "API running 🚀"}