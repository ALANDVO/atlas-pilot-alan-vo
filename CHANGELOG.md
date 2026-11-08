# Changelog

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Added in this checkpoint
- OIDC authentication with Keycloak (PKCE flow)
- PKCE code verifier/challenge generation
- JWT token verification against Keycloak JWKS
- Auth API endpoints: `/auth/login`, `/auth/callback`, `/auth/refresh`, `/auth/logout`, `/auth/me`
- Role-based access control dependencies (`require_role`, `require_any_role`)
- Frontend AuthContext with login, logout, token refresh
- Frontend protected routes with redirect to login
- User info display in dashboard header with logout button

### Changed
- Updated Dashboard to show authenticated user info and roles
- Updated HealthCheck to show auth status
- Updated API client to use HttpOnly cookies (`withCredentials: true`)
- Added KEYCLOAK_REDIRECT_URI to config and .env.example

## [1.0.0] - 2026-10-29

### Added
- Initial project skeleton with FastAPI backend and React + TypeScript + Vite frontend
- Health check endpoint at `/api/v1/health`
- SQLite/PostgreSQL database configuration with SQLAlchemy async
- Docker Compose with backend, frontend, Keycloak, and PostgreSQL
- CI/CD workflow for backend tests and frontend build/test
- Basic frontend dashboard with navigation
- Type-safe API client with axios

### Fixed
- Fixed httpx/pytest-httpx version compatibility
- Fixed react-router-dom Link component usage (to vs href)
- Fixed TypeScript types for vitest globals
- Fixed frontend test setup (globalThis vs global)

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
