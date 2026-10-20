# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

project-skeleton

## Roadmap

### project-skeleton — Project skeleton with FastAPI + React + Vite + Docker + CI

Status: in_progress

Acceptance:
- FastAPI app starts and responds to /health
- React + TypeScript + Vite frontend builds and serves
- Docker compose brings up backend, frontend, Keycloak, PostgreSQL
- CI workflow runs backend tests and frontend build/test
- README with install/run/test steps
- portfolio.json with required fields

### auth-oidc — OIDC authentication with Keycloak (PKCE flow)

Status: planned

Acceptance:
- Login redirects to Keycloak
- Callback exchanges code for tokens with PKCE
- Access token stored in memory only
- Protected API endpoints require valid token
- Logout clears session

### agent-catalog-core — Agent catalog domain engine with CRUD + search + import/export

Status: planned

Acceptance:
- CRUD API for agents with validation
- Search/filter/pagination
- Import from markdown/JSON
- Export to markdown/JSON
- SQLite persistence with audit log

### agent-evaluation-engine — Agent evaluation engine (AI/ML focus)

Status: planned

Acceptance:
- Define evaluation criteria (deterministic)
- Run evaluations against agent responses
- Score and store results
- Compare agents side-by-side
- Export evaluation report

### llm-adapter-framework — LLM adapter framework (OpenAI-compatible, Anthropic, Gemini, Ollama)

Status: planned

Acceptance:
- Unified interface for all providers
- Configurable provider/model/endpoint
- Bounded timeouts and redacted errors
- Keys only server-side

### frontend-dashboard — Frontend dashboard with agent management UI

Status: planned

Acceptance:
- Agent list with search/filter
- Create/edit agent modal
- Agent detail view
- Import/export UI
- Evaluation results view

