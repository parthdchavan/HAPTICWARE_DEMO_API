# HAPTICWARE Demo API

A student-friendly FastAPI backend for managing AI agents with:

- CRUD-style agent operations (create, read, update status)
- Token-based authentication on all agent endpoints
- AI-generated health summaries using OpenRouter
- Supabase/PostgreSQL storage via SQLAlchemy

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL (Supabase)
- OpenRouter API
- Python dotenv

## Project Structure

- main.py: App entry point, table creation, router registration
- config.py: Loads environment variables
- database.py: SQLAlchemy engine, session, base model
- models.py: Database table definitions
- schemas.py: Request body validation models
- routes/agent_routes.py: API endpoints
- services/llm_service.py: AI summary generation service
- auth/auth_handler.py: Bearer token validation
- requirements.txt: Python dependencies
- .env: Secrets and config values

## Environment Variables

Create .env with:

```env
DATABASE_URL=your_postgres_connection
SECRET_TOKEN=your_secret_token
OPENROUTER_API_KEY=your_openrouter_key
```

## Installation

```bash
pip install -r requirements.txt
```

## Run Server

```bash
uvicorn main:app --reload
```

Base URL:

- http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

## Authentication

All agent endpoints require this header:

```http
Authorization: Bearer mysecrettoken
```

Replace mysecrettoken with your SECRET_TOKEN value from .env.

## API Endpoints

### 1) Create Agent

- Method: POST
- URL: /agents
- Headers: Authorization: Bearer <token>
- Body:

```json
{
  "name": "ResumeBot",
  "type": "AI",
  "status": "error"
}
```

- Response includes AI summary:

```json
{
  "id": 1,
  "name": "ResumeBot",
  "type": "AI",
  "status": "error",
  "summary": "Agent is facing issues and may require attention."
}
```

### 2) Get All Agents

- Method: GET
- URL: /agents
- Headers: Authorization: Bearer <token>

- Response:

```json
[
  {
    "id": 1,
    "name": "ResumeBot",
    "type": "AI",
    "status": "error",
    "summary": "Agent is facing issues and may require attention."
  }
]
```

### 3) Update Agent Status

- Method: PUT
- URL: /agents/{agent_id}/status
- Headers: Authorization: Bearer <token>
- Body:

```json
{
  "status": "running"
}
```

- Response includes updated summary.

## Common Errors

- 401 Unauthorized:
  - Missing Authorization header
  - Wrong token format
  - Wrong token value

- 404 Agent not found:
  - Invalid agent_id in status update route

- Missing summary:
  - Check OPENROUTER_API_KEY in .env
  - Verify internet access to OpenRouter
  - Fallback text still appears if LLM call fails

## Quick Curl Test

```bash
curl -H "Authorization: Bearer mysecrettoken" http://127.0.0.1:8000/agents
```

## Notes

- .env is ignored using .gitignore for security.
- Rotate leaked API keys if shared publicly.
