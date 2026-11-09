# BSS Core — S01 Identity & Access

## Overview

**BSS Core** is a modular business management system for authenticated access control, role-based permissions, and module-based authorization. The system implements **S01 Identity & Access** featuring:

- **JWT authentication** with credential-based access for developers and end customers
- **Role-Based Access Control (RBAC)** with least-privilege principle per constitution Section 9.4
- **Argon2id password hashing** per constitution Section 9.2
- **Session management** with timeout and renewal mechanisms
- **Audit logging** of all authentication events
- **Two-application architecture**: backend API (FastAPI) + frontend (Streamlit) with strict separation per constitution Section 3

## Architecture

The system follows **modular monolith** architecture with **Clean Architecture** layer separation (constitution Sections 2-3):

```
src/
├── domain/           # Domain layer — entities, value objects, business rules
│   ├── database.py   # SQLite engine & session management
│   └── auth.py       # Argon2id hashing, JWT, RBAC permissions
├── application/      # Application layer — use cases, services, ports
├── infrastructure/   # Infrastructure layer — repositories, DB implementation
├── presentation/     # Presentation layer — FastAPI routes, Streamlit UI
│   └── frontend/     # Streamlit application (constitution Section 3)
├── api/              # FastAPI application with health check endpoint
└── bss_core/         # Core package
```

## Technology Stack

- **Language**: Python 3.12+
- **Backend**: FastAPI, SQLAlchemy 2.x, Argon2id, PyJWT
- **Frontend**: Streamlit
- **Package Manager**: uv
- **Testing**: pytest (unit, integration, API tests)
- **Linting**: Ruff
- **Database**: SQLite (initial, designed for evolution per constitution Section 7)

## Quickstart

### Prerequisites

- Python 3.12+
- `uv` package manager
- Git

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd bss-core

# 2. Install dependencies
uv sync

# 3. Verify foundation setup
ls specs/002-user-auth/spec.md
ls specs/002-user-auth/plan.md
```

### Running the Applications

**Backend (FastAPI)**:

```bash
python3 -m uvicorn src.api.health:app --host 0.0.0.0 --port 8000
```

Backend available at `http://localhost:8000`:
- `GET /health` — basic health check (`{"status": "ok"}`)
- `GET /health/detailed` — detailed status with version

**Frontend (Streamlit)**:

```bash
streamlit run src/frontend/app.py
```

Frontend available at `http://localhost:8501`:
- Sidebar navigation (Dashboard, Modules, Settings)
- Shows backend connection status
- Communicates with backend through HTTP APIs only

## Implementation Status

All **22 core tasks** across Phases 1-4 are complete:

| Phase | Tasks | Status |
|-------|-------|--------|
| **Phase 1: Setup** | T001-T002 | Complete |
| **Phase 2: Foundational** | T004-T008 | Complete (SQLite, Alembic, JWT auth, layer separation, pytest) |
| **Phase 3: User Story 1** | T010-T014 | Complete (health checks, FastAPI app, Streamlit app, onboarding) |
| **Phase 4: User Story 2** | T015-T022 | Complete (routing, module architecture, layer separation, API endpoints) |

All **14 tests pass** without errors.

## Key Decisions

- **Two-application architecture**: Backend API + Frontend Streamlit with strict HTTP API separation (constitution Section 3)
- **SQLite initial database**: Designed for evolution to production data stores per constitution Section 7
- **JWT authentication**: Centralized authentication mechanism (constitution Section 9)
- **Argon2id password hashing**: Industry-standard password hashing per constitution Section 9.2
- **RBAC least-privilege**: Role-based access control with minimum necessary permissions (constitution Section 9.4)
- **Technology-agnostic specifications**: All success criteria measurable without implementation details

## Sprints

The system is delivered across 7 sprints (S00–S07):

- **S00** — Project Foundation
- **S01** — Identity & Access *(current)*
- **S02** — Customer Management
- **S03** — Order Management
- **S04** — Shipment Management
- **S05** — Billing Management
- **S06** — Dashboard & Reporting
- **S07** — Integration & MVP Release

## License

MIT License — see LICENSE file for details.