# Quickstart Validation Guide: Project Foundation

## Purpose

Provide runnable validation scenarios that prove the Project Foundation feature works end-to-end. This guide serves as the acceptance test checklist for the specification. It references the data model and contracts rather than duplicating them.

## Prerequisites

- Git installed
- Python 3.12+ installed
- `uv` package manager installed
- Repository cloned from the project root

## Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd bss-core

# 2. Initialize the feature foundation
uv init
# This creates the pyproject.toml and project structure

# 3. Run the foundation setup script
bash .specify/scripts/bash/setup-plan.sh --json
# This copies the plan template and outputs feature directory information

# 4. Verify the feature directory was created
ls -la specs/001-project-foundation/
```

## Validation Scenarios

### Scenario 1: Repository and Project Initialization

**Goal**: Verify that the development environment is properly initialized.

**Steps**:

1. Ensure the repository is initialized with proper project metadata
2. Verify the `uv` project file (`pyproject.toml`) exists and has correct configuration
3. Check that the project structure includes the expected directories

**Expected Outcome**:

- Repository has `pyproject.toml` with project metadata
- `specs/001-project-foundation/` directory exists containing `spec.md`
- `uv` version is resolvable without errors

**Validation Command**:

```bash
uv --version
ls specs/001-project-foundation/spec.md
```

---

### Scenario 2: FastAPI Backend Health Check

**Goal**: Verify the FastAPI backend application starts and responds to a health check endpoint.

**Steps**:

1. Start the FastAPI application
2. Send a GET request to the health check endpoint
3. Verify the response status and content

**Expected Outcome**:

- FastAPI application starts without errors
- Health check endpoint responds within 2 seconds (SC-002)
- Response indicates service is operational

**Validation Command** (approximate, depending on actual FastAPI scaffold):

```bash
# Start the server (example)
uv run uvicorn app:app --host 0.0.0.0 --port 8000

# Test the health check
curl http://localhost:8000/health
# Expected: {"status": "ok"} or similar response
```

---

### Scenario 3: Streamlit Frontend Startup

**Goal**: Verify the Streamlit frontend application starts without errors.

**Steps**:

1. Start the Streamlit application
2. Verify it loads without Python errors
3. Check that the basic interface is displayed

**Expected Outcome**:

- Streamlit application starts without errors (SC-003)
- Basic welcome page or interface loads
- No import errors or configuration failures

**Validation Command** (example):

```bash
streamlit run streamlit_app.py
# Expected: Browser opens with Streamlit interface, no Python tracebacks
```

---

### Scenario 4: Module Structure Initialization

**Goal**: Verify all five initial modules have their directory structure created.

**Steps**:

1. Check that the five module directories exist with expected layer separation
2. Verify each module has Domain, Application, Infrastructure, and Presentation components

**Expected Outcome**:

- Five module directories exist: Identity & Access, Customer Management, Order Management, Shipment Management, Billing Management
- Each module has the expected layered architecture
- Module structure aligns with the spec's FR-008 requirements

**Validation Command** (directory inspection):

```bash
ls specs/001-project-foundation/
# Expected to see module-related structure per the spec
```

---

### Scenario 5: Test Execution

**Goal**: Verify pytest can be executed without errors.

**Steps**:

1. Run pytest on the project
2. Verify it completes without errors (even if no tests are defined yet per SC-005)

**Expected Outcome**:

- `pytest` executes and runs without errors
- No configuration errors
- Test collection completes successfully

**Validation Command**:

```bash
pytest --collect-only
# Expected: Collection completes; may show "no tests collected" if no tests defined yet, but no errors
```

---

### Scenario 6: Linting Validation

**Goal**: Verify Ruff linting passes with no failures.

**Steps**:

1. Run ruff on the project codebase
2. Verify no linting or formatting failures

**Expected Outcome**:

- `Ruff` linting passes with no failures (SC-006)
- No code style issues detected
- Consistent with project quality standards

**Validation Command**:

```bash
ruff check .
# Expected: No output (no issues found) or only informational messages
```

---

## References

- **Data Model**: See `data-model.md` for entity definitions, attributes, and relationships
- **Success Criteria**: See spec `specs/001-project-foundation/spec.md` Section "Measurable Outcomes" (SC-001 through SC-009)
- **Functional Requirements**: See spec `specs/001-project-foundation/spec.md` Section "Functional Requirements" (FR-001 through FR-010)
- **Assumptions**: See spec `specs/001-project-foundation/spec.md` Section "Assumptions"
- **Constitution**: See `.specify/memory/constitution.md` for architectural standards and principles

## Notes

- These validation scenarios are minimal and focus on proving the foundation is properly set up
- Full implementation validation (business logic, API contracts, database migrations) belongs to subsequent sprints (S01-S07)
- Each scenario maps to a success criterion or functional requirement in the specification
- If any scenario fails, review the corresponding specification section and assumptions