# BSS Core — Documentation

## 1. Overview

This directory contains the technical, architectural, functional, and operational documentation for **BSS Core**.

BSS Core is a modular business management system designed to manage core business operations, including:

- Customer Management
- Order Management
- Shipment Management
- Billing Management
- User Management and Authentication

The project follows:

- Domain-Driven Design (DDD)
- Clean Architecture
- Modular Monolith Architecture
- REST API architecture
- Specification-Driven Development (SDD)

The documentation is the reference for developers, architects, reviewers, and AI coding agents working on the project.

## 2. Documentation Principles

All project documentation must follow these principles:

1. Maintain a single source of truth for each subject.
2. Document architectural decisions explicitly.
3. Separate business requirements from technical implementation.
4. Keep documentation synchronized with the implementation.
5. Prefer simple, maintainable solutions over unnecessary complexity.
6. Use specifications to define individual features before implementation.
7. Avoid duplicating information between `docs/` and `specifications/`.

### Documentation ownership

| Information | Location |
|---|---|
| Product vision and scope | `product.md` |
| Business domain and modules | `domain.md` |
| System architecture | `architecture.md` |
| Technical decisions | `decisions.md` |
| Database conventions | `database.md` |
| API conventions | `api.md` |
| Security requirements | `security.md` |
| Testing strategy | `testing.md` |
| Development workflow | `development.md` |
| Data generation | `data-generation.md` |
| Feature requirements | `../specifications/` |

## 3. Documentation Structure

The documentation directory must remain flat.

```text
docs/
├── README.md
├── product.md
├── domain.md
├── architecture.md
├── decisions.md
├── database.md
├── api.md
├── security.md
├── testing.md
├── development.md
└── data-generation.md
```

### Document descriptions

| Document | Responsibility |
|---|---|
| `README.md` | Documentation index and guidelines |
| `product.md` | Product vision, objectives, scope, users and requirements |
| `domain.md` | Business domains, bounded contexts, entities and business rules |
| `architecture.md` | System architecture, application boundaries and architectural patterns |
| `decisions.md` | Architecture Decision Records (ADRs) and important technical decisions |
| `database.md` | Database design, persistence conventions and migrations |
| `api.md` | REST API conventions, endpoints, request/response contracts and error handling |
| `security.md` | Authentication, authorization, RBAC and security requirements |
| `testing.md` | Testing strategy, test levels and quality standards |
| `development.md` | Local setup, coding standards, Git workflow and development commands |
| `data-generation.md` | Synthetic data generation, scenarios, reproducibility and database initialization |

## 4. Business Modules

BSS Core is organized around business capabilities.

| Module | Main responsibilities |
|---|---|
| Identity & Access | User accounts, authentication, authorization, roles and permissions |
| Customer | Customer profiles, contacts, addresses and customer lifecycle |
| Order | Order creation, order items, order status and order lifecycle |
| Shipment | Shipment creation, delivery information, tracking and shipment status |
| Billing | Invoices, payments, billing status and financial transactions |

Each module owns its business rules and domain logic.

Modules must communicate through explicit application interfaces rather than accessing another module's internal implementation.

Additional supporting capabilities may be introduced when justified by business requirements.

## 5. Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Dependency management | uv |
| Backend API | FastAPI |
| ORM | SQLAlchemy 2.x |
| Database migrations | Alembic |
| Initial database | SQLite |
| Frontend | Streamlit |
| Testing | pytest |
| Code quality | Ruff |
| Architecture | DDD + Clean Architecture |
| Development methodology | Spec Kit (SDD) |

### Application separation

The project contains two independent applications:

- `bss_core_api`: Backend application responsible for business logic, persistence, authentication and REST APIs.
- `bss_core_app`: Streamlit application responsible for the user interface.

The Streamlit application must communicate with the backend exclusively through HTTP APIs.

It must never access the database or backend repositories directly.

## 6. Specification-Driven Development

BSS Core uses Spec Kit to implement features through a specification-first workflow.

Specifications are maintained separately from general project documentation.

### Specifications directory

```text
specifications/
├── 001-identity-access/
├── 002-customer-management/
├── 003-order-management/
├── 004-shipment-management/
└── 005-billing-management/
```

Each feature specification may contain:

```text
001-identity-access/
├── spec.md
├── plan.md
├── tasks.md
├── research.md
├── data-model.md
├── contracts/
└── checklists/
```

The exact files depend on the feature and its complexity.

### Feature development workflow

Every feature follows this lifecycle:

1. Define the business problem.
2. Create the feature specification.
3. Identify functional and non-functional requirements.
4. Define acceptance criteria.
5. Create the technical implementation plan.
6. Define architecture and data contracts.
7. Generate implementation tasks.
8. Implement the feature.
9. Run automated tests.
10. Validate acceptance criteria.
11. Update relevant documentation.

### Important rule

`docs/` describes the overall product, architecture, standards and conventions.

`specifications/` describes individual features and their implementation requirements.

Do not duplicate complete feature specifications inside `docs/`.

## 7. Data Generation

BSS Core includes a dedicated synthetic data generator.

Its purpose is to create realistic, interconnected business data for development, testing and demonstrations.

Location:

```text
tools/
└── data_generator/
```

The generator must support:

- Configurable record volumes.
- Reproducible data generation using random seeds.
- Customer, order, shipment and billing relationships.
- Referential integrity.
- Dependency-aware generation order.
- Realistic business scenarios.
- Database initialization and reset.
- Domain validation.

The generator is a development utility, not a production business service.

See `data-generation.md`.

## 8. Architecture and Documentation Rules

All implementation and documentation must respect these rules:

### Architecture

- Follow Clean Architecture dependency rules.
- Keep domain logic independent of frameworks.
- Use explicit module boundaries.
- Keep business rules inside the appropriate domain.
- Avoid unnecessary cross-module dependencies.
- Keep the system a modular monolith unless an architectural decision justifies otherwise.

### Backend

- FastAPI exposes REST APIs.
- SQLAlchemy handles persistence.
- Alembic manages schema migrations.
- Authentication and authorization are enforced by the backend.
- Business validation must not depend on Streamlit.

### Frontend

- Streamlit handles presentation and user interaction.
- API communication happens through HTTP.
- No direct database connections.
- No duplication of backend business rules.

### Testing

- Unit tests for domain logic.
- Integration tests for persistence and application services.
- API tests for HTTP contracts and authorization.
- End-to-end tests for important business workflows.

## 9. AI Coding Agent Instructions

AI coding agents working on BSS Core must follow these rules:

1. Read this documentation before starting a feature.
2. Read the relevant domain and architecture documents.
3. Read the corresponding feature specification.
4. Do not invent business requirements.
5. Do not modify architectural boundaries without justification.
6. Do not implement functionality outside the approved specification.
7. Follow the project's existing naming and coding conventions.
8. Write tests for implemented functionality.
9. Run relevant quality checks before declaring a task complete.
10. Update documentation when implementation changes documented behavior.

### Required implementation discipline

Before writing code, the agent must understand:

- What business problem is being solved?
- Which module owns the functionality?
- What are the domain rules?
- Which application layer is responsible?
- What API contract is required?
- What data changes are necessary?
- What tests demonstrate correctness?

If requirements are ambiguous, identify the ambiguity instead of making unsupported assumptions.

## 10. Keeping Documentation Updated

Documentation must evolve with the system.

| Change | Required documentation update |
|---|---|
| New business capability | `domain.md` and feature specification |
| Architecture change | `architecture.md` and `decisions.md` |
| Database schema change | `database.md` |
| API contract change | `api.md` |
| Authentication or authorization change | `security.md` |
| Testing strategy change | `testing.md` |
| Development workflow change | `development.md` |
| Data generation change | `data-generation.md` |

Documentation changes should be included in the same feature delivery whenever possible.

## 11. Definition of Done

A feature is considered complete when:

- Its specification has been implemented.
- Acceptance criteria have been verified.
- Domain and application logic follow the architecture.
- Database changes have appropriate migrations.
- API contracts are implemented and tested.
- Automated tests pass.
- Ruff checks pass.
- Security requirements are satisfied.
- Relevant documentation is updated.
- No unrelated functionality has been introduced.

---

**BSS Core — Documentation is the reference for understanding, building, testing and maintaining the system.**
