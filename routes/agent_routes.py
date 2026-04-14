from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.auth_handler import verify_token
from database import SessionLocal
from models import Agent
from schemas import AgentCreate, StatusUpdate
from services.llm_service import generate_summary, generate_api_info

router = APIRouter()


# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST /agents
@router.post("/agents")
def create_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    summary = generate_summary(agent.status)

    new_agent = Agent(
        name=agent.name,
        type=agent.type,
        status=agent.status,
        summary=summary,
    )

    db.add(new_agent)      # add to DB
    db.commit()            # save
    db.refresh(new_agent)  # get updated data (id)

    return {
        "id": new_agent.id,
        "name": new_agent.name,
        "type": new_agent.type,
        "status": new_agent.status,
        "summary": new_agent.summary,
    }


# GET /agents
@router.get("/agents")
def get_agents(
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    agents = db.query(Agent).all()

    result = []
    changed = False
    for agent in agents:
        if not agent.summary:
            agent.summary = generate_summary(agent.status)
            changed = True

        result.append(
            {
                "id": agent.id,
                "name": agent.name,
                "type": agent.type,
                "status": agent.status,
                "summary": agent.summary,
            }
        )

    if changed:
        db.commit()

    return result


@router.put("/agents/{agent_id}/status")
def update_status(
    agent_id: int,
    update: StatusUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.status = update.status
    agent.summary = generate_summary(update.status)

    db.commit()
    db.refresh(agent)

    return {
        "id": agent.id,
        "name": agent.name,
        "type": agent.type,
        "status": agent.status,
        "summary": agent.summary,
    }


@router.get("/ai/api-info")
def get_api_information(_: str = Depends(verify_token)):
    try:
        info = generate_api_info()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable: {str(e)}",
        )

    return {
        "topic": "What is API and how it works",
        "answer": info,
    }
