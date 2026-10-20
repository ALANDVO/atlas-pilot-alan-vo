# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

# CHANGELOG

## [1.0.0] - 2026-10-20

### Added
- Initial project skeleton with FastAPI backend and React + TypeScript + Vite frontend
- Health check endpoint at `/api/v1/health`
- SQLite/PostgreSQL database configuration with SQLAlchemy async
- Docker Compose with backend, frontend, Keycloak, and PostgreSQL
- CI/CD workflow for backend tests and frontend build/test
- Basic frontend dashboard with navigation
- Type-safe API client with axios