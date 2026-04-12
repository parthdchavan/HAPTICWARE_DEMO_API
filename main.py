from fastapi import FastAPI
from database import engine, Base
import models
from routes.agent_routes import router as agent_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(agent_router)

@app.get("/")
def home():
    return {"message": "API running 🚀"}