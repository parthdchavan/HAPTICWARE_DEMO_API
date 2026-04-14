# HAPTICWARE Demo API — Full Walkthrough Guide

This file is your 10-minute verbal walkthrough companion.
It explains every file, every concept, and how everything connects.

---

## What Did We Build?

A REST API that manages AI agents. Think of an "agent" like a bot or a service running somewhere.
This API lets you:

- Create an agent
- List all agents
- Update an agent's status

And for every agent, it automatically generates a human-readable health summary using an LLM (AI).
All endpoints are protected — you must send a secret token to use them.

---

## The Big Picture (Request Flow)

```
Client sends HTTP request
        ↓
FastAPI receives it (main.py)
        ↓
Auth check runs first (auth_handler.py) → 401 if token is wrong
        ↓
Route handler runs (agent_routes.py)
        ↓
DB session opens (database.py + models.py)
        ↓
AI summary is generated (llm_service.py)
        ↓
Data saved to PostgreSQL (Supabase)
        ↓
Response returned to client
```

---

## File-by-File Explanation

---

### 1. `.env` — Secrets File

```env
DATABASE_URL=your_postgres_connection
SECRET_TOKEN=your_secret_token
OPENROUTER_API_KEY=your_openrouter_key
```

- This file is NEVER committed to git (it's in `.gitignore`)
- It holds all sensitive values: DB password, API keys, auth token
- Every other file reads from here via `config.py`

**Say this:** ".env is where all secrets live. We never hardcode passwords in code."

---

### 2. `config.py` — Environment Variable Loader

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set.")
```

**What it does:**
- `load_dotenv()` reads the `.env` file and loads values into environment
- `os.getenv()` fetches each value by name
- If `DATABASE_URL` is missing, the app crashes immediately with a clear error — this is intentional, so you don't get a confusing DB error later

**Say this:** "config.py is the single place where all environment variables are loaded. Every other file imports from here, so secrets are centralized."

---

### 3. `database.py` — Database Connection Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

**Three things created here:**

| Object | What it is | Used for |
|---|---|---|
| `engine` | The actual DB connection | Talks to PostgreSQL |
| `SessionLocal` | A session factory | Opens/closes DB sessions per request |
| `Base` | SQLAlchemy base class | All models inherit from this |

- `sslmode: require` is needed because Supabase (cloud PostgreSQL) requires SSL
- `SessionLocal` is a factory — calling `SessionLocal()` gives you a new session

**Say this:** "database.py sets up the connection to PostgreSQL. The engine is the connection, SessionLocal creates sessions per request, and Base is what our models extend."

---

### 4. `models.py` — Database Table Definition

```python
from sqlalchemy import Column, Integer, String
from database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    summary = Column(String, nullable=True)
```

**What it does:**
- Defines the `agents` table in PostgreSQL using Python class syntax
- Each `Column` maps to a column in the database
- `primary_key=True` means `id` auto-increments
- `nullable=False` means the field is required
- `summary` is `nullable=True` because it's generated after creation

**Say this:** "models.py is the Python representation of our database table. SQLAlchemy maps this class to an actual PostgreSQL table automatically."

---

### 5. `schemas.py` — Request Body Validation

```python
from pydantic import BaseModel

class AgentCreate(BaseModel):
    name: str
    type: str
    status: str

class StatusUpdate(BaseModel):
    status: str
```

**What it does:**
- Pydantic models validate incoming JSON before the route logic runs
- If a required field is missing or wrong type, FastAPI returns a 422 error automatically
- `AgentCreate` is used for `POST /agents`
- `StatusUpdate` is used for `PUT /agents/{id}/status`

**Difference from models.py:**
- `models.py` = database shape (what's stored)
- `schemas.py` = API shape (what the client sends)

**Say this:** "schemas.py validates the request body. If someone sends wrong data, FastAPI rejects it before our code even runs."

---

### 6. `auth/auth_handler.py` — Token Authentication

```python
from fastapi import Header, HTTPException
from config import SECRET_TOKEN

def verify_token(authorization: Optional[str] = Header(default=None)):
    if not SECRET_TOKEN:
        raise HTTPException(status_code=500, detail="Server token is not configured")

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or parts[1] != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return parts[1]
```

**How it works step by step:**

1. FastAPI reads the `Authorization` header from the request
2. If header is missing → 401
3. Splits the header: `"Bearer mysecrettoken"` → `["Bearer", "mysecrettoken"]`
4. Checks format is exactly 2 parts, first part is "bearer", second matches `SECRET_TOKEN`
5. If anything is wrong → 401 Unauthorized
6. If valid → returns the token (used as a signal that auth passed)

**Say this:** "auth_handler.py is our security layer. It reads the Authorization header, validates the Bearer token format, and compares it to our secret. Any mismatch returns 401."

---

### 7. `services/llm_service.py` — AI Summary Generator

```python
import requests
from config import OPENROUTER_API_KEY

def generate_summary(status):
    try:
        prompt = f"""
        You are an AI monitoring assistant.
        Given the agent status: {status}
        Generate a short one-line health summary.
        """

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=10,
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception:
        return f"Status is {status}"   # fallback
```

**How it works:**

1. Takes `status` as input (e.g., `"error"`, `"running"`)
2. Builds a prompt asking the LLM to generate a one-line health summary
3. Calls OpenRouter API (which routes to GPT-3.5-turbo)
4. Parses the response: `data["choices"][0]["message"]["content"]`
5. If anything fails (network, API key, timeout) → returns a safe fallback string

**Why OpenRouter?** It's a unified API gateway for multiple LLMs. One API key, many models.

**Say this:** "llm_service.py is the AI layer. It takes a status string, sends it to GPT-3.5-turbo via OpenRouter, and returns a human-readable summary. The try/except ensures the API never crashes if the LLM is unavailable."

---

### 8. `routes/agent_routes.py` — API Endpoints

This is the core of the API. Three endpoints live here.

#### DB Session Dependency

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- Opens a DB session at the start of each request
- `yield` gives the session to the route
- `finally` ensures the session is always closed, even if an error occurs
- This is the dependency injection pattern in FastAPI

---

#### POST /agents — Create Agent

```python
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

    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    return {"id": new_agent.id, "name": ..., "summary": ...}
```

**Flow:**
1. `Depends(verify_token)` runs auth check first
2. `Depends(get_db)` opens DB session
3. Pydantic validates `agent` body automatically
4. Calls `generate_summary()` to get AI text
5. Creates `Agent` object, adds to DB, commits, refreshes (to get the auto-generated `id`)
6. Returns the full agent with summary

---

#### GET /agents — List All Agents

```python
@router.get("/agents")
def get_agents(db: Session = Depends(get_db), _: str = Depends(verify_token)):
    agents = db.query(Agent).all()

    result = []
    changed = False
    for agent in agents:
        if not agent.summary:
            agent.summary = generate_summary(agent.status)
            changed = True
        result.append({...})

    if changed:
        db.commit()

    return result
```

**Smart detail:** If any agent in the DB is missing a summary (e.g., old data), it generates one on the fly and saves it. This is a backfill pattern.

---

#### PUT /agents/{agent_id}/status — Update Status

```python
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

    return {...}
```

**Flow:**
1. `agent_id` comes from the URL path
2. Queries DB for that specific agent
3. If not found → 404
4. Updates status and regenerates summary
5. Commits and returns updated agent

---

### 9. `main.py` — App Entry Point

```python
from fastapi import FastAPI
from database import engine, Base
from sqlalchemy import text
import models
from routes.agent_routes import router as agent_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

with engine.begin() as conn:
    conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS summary VARCHAR"))

app.include_router(agent_router)

@app.get("/")
def home():
    return {"message": "API running 🚀"}
```

**What happens on startup:**

1. `FastAPI()` creates the app instance
2. `Base.metadata.create_all()` creates the `agents` table if it doesn't exist
3. The `ALTER TABLE` line adds the `summary` column to existing databases that were created before the column was added — this is a safe migration
4. `include_router()` mounts all routes from `agent_routes.py`
5. The `/` route is a health check

**Say this:** "main.py is the entry point. It creates the app, runs DB migrations on startup, and registers all routes."

---

## How Dependency Injection Works (Key Concept)

FastAPI's `Depends()` is the most important pattern in this project.

```python
def create_agent(
    agent: AgentCreate,           # from request body
    db: Session = Depends(get_db),       # DB session injected
    _: str = Depends(verify_token),      # auth check injected
):
```

- FastAPI sees `Depends(get_db)` and calls `get_db()` automatically
- FastAPI sees `Depends(verify_token)` and calls `verify_token()` automatically
- If `verify_token` raises a 401, the route function never runs
- This keeps route logic clean — no manual auth checks inside every function

---

## How the Summary Column Was Added Safely

The `summary` column was added after the initial table was created.
Instead of dropping and recreating the table (which loses data), we used:

```python
conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS summary VARCHAR"))
```

- `IF NOT EXISTS` means it won't crash if the column already exists
- This runs every time the server starts — it's idempotent (safe to run multiple times)

---

## Error Handling Summary

| Scenario | HTTP Code | Where it's handled |
|---|---|---|
| Missing Authorization header | 401 | auth_handler.py |
| Wrong token | 401 | auth_handler.py |
| Agent ID not found | 404 | agent_routes.py |
| Missing request body field | 422 | Pydantic (automatic) |
| LLM API failure | No crash | llm_service.py try/except |
| DATABASE_URL missing | 500 (startup crash) | config.py |

---

## What to Say During the 10-Minute Walkthrough

### Minute 1-2: Overview
"This is a FastAPI backend for agent health monitoring. It has three endpoints, token auth, and AI-generated summaries. Let me walk through each file."

### Minute 3: config + database + models
"config.py loads secrets. database.py sets up the SQLAlchemy connection to Supabase PostgreSQL. models.py defines the agents table as a Python class."

### Minute 4: schemas + auth
"schemas.py validates request bodies using Pydantic. auth_handler.py reads the Authorization header, checks the Bearer token format, and returns 401 if anything is wrong."

### Minute 5-6: llm_service
"llm_service.py calls OpenRouter's API with a prompt built from the agent's status. It parses the response and returns a one-line summary. If the call fails, it returns a fallback string so the API never crashes."

### Minute 7-8: routes
"agent_routes.py has three endpoints. POST creates an agent and generates a summary. GET lists all agents and backfills missing summaries. PUT updates status and regenerates the summary. All three use Depends() for auth and DB injection."

### Minute 9: main.py
"main.py starts the app, runs table creation and the summary column migration on startup, and mounts the router."

### Minute 10: Demo
- Hit GET /agents without token → show 401
- Hit GET /agents with token → show agent list with summaries
- POST a new agent with status "error" → show AI summary in response
- PUT to update status to "running" → show summary changes

---

## One-Line Answers for Common Questions

**Q: Why FastAPI over Flask?**
A: FastAPI has built-in Pydantic validation, async support, and auto-generates Swagger docs.

**Q: Why SQLAlchemy instead of raw SQL?**
A: It maps Python objects to DB rows, handles sessions, and prevents SQL injection.

**Q: Why OpenRouter instead of OpenAI directly?**
A: OpenRouter is a unified gateway — one API key works for many models including GPT, Claude, Mistral.

**Q: What happens if the LLM is down?**
A: The `except` block in `llm_service.py` returns a fallback string. The API keeps working.

**Q: How is the token validated?**
A: The Authorization header must be exactly `Bearer <SECRET_TOKEN>`. Any deviation returns 401.

**Q: What is `Depends()` in FastAPI?**
A: It's dependency injection. FastAPI calls the dependency function automatically and injects the result into the route. If the dependency raises an exception, the route never runs.
