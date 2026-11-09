# BSS Core — Project Foundation

## Overview

**BSS Core** is a modular business management system designed to manage customer relationships, products and services, orders, shipments, billing, users, and supporting business operations.

The system follows a **modular monolith architecture** with **Domain-Driven Design (DDD)** and **Clean Architecture** principles, maintaining a clear separation between:

- **Backend API** (FastAPI) — owns business operations, authentication, validation, persistence, and versioned REST endpoints
- **Frontend Application** (Streamlit) — provides the user interface, communicating with the backend exclusively through HTTP APIs

## Project Structure

```
bss-core/
├── .specify/              # Specification and configuration hub
├── docs/                  # Project documentation and sprint planning
├── specs/                 # Feature specifications
│   └── 001-project-foundation/  # S00: Project Foundation
├── specs/001-project-foundation/
│   ├── plan.md            # Implementation plan
│ ├── research.md          # Phase 0 research findings
│ ├── data-model.md        # Entity-relationship model
│ ├── quickstart.md        # Validation guide
│ ├── tasks.md             # 26 implementation tasks across 5 phases
│ ├── spec.md              # Feature specification
│ └── contracts/           # API contract specifications
├── src/                   # Source code (single project layout)
│   ├── models/            # SQLAlchemy models and entities
│   ├── services/          # Business use-case services
│   ├── api/               # FastAPI route handlers
│   └── lib/               # Shared library code
├── tests/                 # Test suites
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── contract/          # Contract tests
├── pyproject.toml         # Project configuration with uv
├── .gitignore
└── README.md              # This file
```

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

# 2. Initialize the feature foundation
uv init
bash .specify/scripts/bash/setup-plan.sh --json

# 2. Install dependencies
uv sync

# 3. Verify the foundation is set up
ls specs/001-project-foundation/spec.md
```

### Running the Applications

**Backend (FastAPI)**:

```bash
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

**Frontend (Streamlit)**:

```bash
streamlit run streamlit_app.py
```

## Development

### Project Phases

The implementation follows a phased approach:

1. **Phase 1: Setup** — Project initialization and basic structure
2. **Phase 2: Foundational** — Blocking prerequisites (MUST complete before user stories)
3. **Phase 3: User Story 1 (P1)** — MVP: Development environment for developers and end customers
4. **Phase 4: User Story 2 (P2)** — Architecture foundation with layer-separated modules
5. **Phase 5: Polish** — Cross-cutting concerns, documentation, performance optimization

### Key Decisions

- **Language/Framework**: Python 3.12+ with FastAPI, SQLAlchemy 2.x, Streamlit
- **Database**: SQLite (initial, designed for evolution to other databases per constitution)
- **Architecture**: Modular monolith with DDD and Clean Architecture (constitution Sections 2-3)
- **Authentication**: JWT with Argon2id password hashing (constitution Section 9.2)
- **Testing**: pytest with unit, integration, and API test support (constitution Section 10)

## Sprints

The system is delivered across 7 sprints (S00–S07):

- **S00** — Project Foundation (this feature)
- **S01** — Identity & Access
- **S02** — Customer Management
- **S03** — Order Management
- **S04** — Shipment Management
- **S05** — Billing Management
- **S06** — Dashboard & Reporting
- **S07** — Integration & MVP Release

## License

MIT License — see LICENSE file for details.