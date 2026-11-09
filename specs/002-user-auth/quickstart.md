# Quickstart Validation Guide: S01 Identity & Access

## Purpose

Provide runnable validation scenarios that prove the S01 Identity & Access feature works end-to-end. This guide serves as the acceptance test checklist for the specification. It references the data model and contracts rather than duplicating them.

## Prerequisites

- Git installed
- Python 3.12+ installed
- `uv` package manager installed
- Repository cloned from the project root

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd bss-core
```

### 2. Initialize the feature

```bash
uv init
# This creates the pyproject.toml and project structure
```

### 3. Run the plan setup script

```bash
bash .specify/scripts/bash/setup-plan.sh --json
# This copies the plan template and outputs feature directory information
```

### 4. Verify the feature directory was created

```bash
ls -la specs/002-user-auth/
# Expected: spec.md, plan.md, research.md, data-model.md, quickstart.md, checklists/, contracts/
```

## Validation Scenarios

### Scenario 1: Specification and Project Initialization

**Goal**: Verify that the development environment is properly initialized and the S01 specification is accessible.

**Steps**:

1. Ensure the repository is initialized with proper project metadata
2. Verify the `uv` project file (`pyproject.toml`) exists and has correct configuration
3. Check that the specification directory exists and contains required files
4. Confirm the plan template was copied successfully

**Expected Outcome**:

- Repository has `pyproject.toml` with project metadata
- `specs/002-user-auth/` directory exists containing `spec.md`
- `plan.md` is present with technical context and constitution check PASSED
- `research.md` is present with all clarifications resolved
- `data-model.md` is present with User, Role, and Session entities
- `uv` version is resolvable without errors

**Validation Command**:

```bash
uv --version
ls specs/002-user-auth/spec.md
ls specs/002-user-auth/plan.md
ls specs/002-user-auth/research.md
ls specs/002-user-auth/data-model.md
```

---

### Scenario 2: User Entity Validation

**Goal**: Verify the User entity structure and attributes are correctly defined.

**Steps**:

1. Read the User entity definition from `data-model.md`
2. Confirm all required attributes are present (id, username, email, role, status, created_at, last_login, failed_attempts, locked_until)
3. Verify identity rules (username uniquely identified within system scope)
4. Check relationship definitions (User has one Role, belongs to many Sessions)

**Expected Outcome**:

- User entity has all 9 attributes as documented
- Username is uniquely identified within system scope
- User-Role relationship (many-to-one) is documented
- User-Session relationship (one-to-many) is documented

**Validation Command** (manual review):

```bash
# Review data-model.md User entity section
# Expected: All 9 attributes present with correct types and identity rules
```

---

### Scenario 3: Role Entity Validation

**Goal**: Verify the Role entity structure and permission mappings.

**Steps**:

1. Read the Role entity definition from `data-model.md`
2. Confirm all required attributes are present (id, name, description, permissions, created_at, updated_at)
3. Verify module access levels (Identity & Access, Customer Management, Order Management, Shipment Management, Billing Management)
4. Check relationship definitions (Role has many Users, permissions map to module boundaries)

**Expected Outcome**:

- Role entity has all 6 attributes as documented
- Role name is uniquely identified within system scope
- Permissions map to 5 module access levels
- Role-User relationship (one-to-many) is documented

**Validation Command** (manual review):

```bash
# Review data-model.md Role entity section
# Expected: All 6 attributes present with correct types and permission mappings
```

---

### Scenario 4: Session Entity Validation

**Goal**: Verify the Session entity structure and user-session relationships.

**Steps**:

1. Read the Session entity definition from `data-model.md`
2. Confirm all required attributes are present (id, user_id, created_at, expires_at, revoked_at, ip_address, user_agent)
3. Verify identity rules (session ID uniquely identified within system scope)
4. Check relationship definitions (Session belongs to one User, user has many Sessions)

**Expected Outcome**:

- Session entity has all 7 attributes as documented
- Session ID is uniquely identified within system scope
- Session-User relationship (many-to-one) is documented
- User-Session relationship (one-to-many) is documented

**Validation Command** (manual review):

```bash
# Review data-model.md Session entity section
# Expected: All 7 attributes present with correct types and relationship rules
```

---

### Scenario 5: Contract Documentation Review

**Goal**: Verify that interface contracts are documented in the contracts/ directory.

**Steps**:

1. Check if `contracts/` directory exists
2. Review any contract documentation present
3. Verify contracts reference the data model entities (User, Role, Session)
4. Confirm contract format is appropriate for the project type (internal business system)

**Expected Outcome**:

- `contracts/` directory exists (may be empty for internal-only system)
- Any contract documentation references data model entities
- Contract format aligns with internal business system patterns

**Validation Command** (manual review):

```bash
# Check contracts/ directory exists
ls specs/002-user-auth/contracts/
# Review any documentation present
# Expected: Directory exists; contracts reference data model if present
```