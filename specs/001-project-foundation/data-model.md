# Data Model: Project Foundation

## Entities

### Project

- **Description**: The root organizational unit containing configuration, metadata, and shared setup for the entire system.
- **Attributes**:
  - `id`: Unique identifier (primary key)
  - `name`: Project name; unique within system scope
  - `created_at`: Timestamp of project creation
  - `status`: Current project status (e.g., "active", "archived", "initializing")
- **Identity**: Uniquely identified by `name` within the system
- **Relationships**: 
  - Owns one or more `Module` entities (one-to-many)
  - Modules belong to exactly one `Project`

### Module

- **Description**: A business capability boundary that owns its domain logic, repositories, and API endpoints. Supports the modular monolith architecture with layer separation (Domain, Application, Infrastructure, Presentation).
- **Attributes**:
  - `id`: Unique identifier (primary key)
  - `name`: Module name; unique within its parent Project's scope
  - `project_id`: Foreign key referencing the parent Project
  - `status`: Current module status (e.g., "initialized", "in-development", "complete")
- **Identity**: Uniquely identified by `name` within its parent Project's scope
- **Relationships**:
  - Belongs to exactly one `Project` (many-to-one)
  - Owns its own domain layer entities and value objects
  - Exposes application-level use cases/ports
  - Infrastructure layer implements repositories for this module's domain entities
  - Presentation layer (FastAPI routes) for this module's API endpoints

## Relationships

### Project ↔ Module (One-to-Many)

- **Project**: One project can have multiple modules
- **Module**: Each module belongs to exactly one project
- **Cardinality**: 1 Project → N Modules
- **Deletion**: Project deletion requires cascading module reassignment or deprecation (deferred to module-level design)

## Validation Rules (from Functional Requirements)

Per the functional requirements in the feature specification:

- **FR-001**: Project must have initialization metadata and version control tracking
- **FR-002**: Project dependency management must be consistent across the system
- **FR-005**: Database connection and session management must be configured for persistence
- **FR-006**: Database migration infrastructure must be version-controlled
- **FR-007**: Layer separation (Domain, Application, Infrastructure, Presentation) must be maintained
- **FR-008**: Module structure must organize business capabilities into bounded contexts
- **FR-009**: Unit and integration testing must be available from project start
- **FR-010**: Linting and formatting standards must be enforced automatically

## State Transitions (if applicable)

### Project States

- `initializing` → Project is being set up (repository initialized, uv project file created)
- `active` → Project is ready for module development; developer onboarding complete
- `deprecating` → Project modules are being migrated or replaced

### Module States

- `initialized` → Module directory structure created; layer separation established
- `in-development` → Domain logic, use cases, and API endpoints under active development
- `complete` → Module business logic, repositories, and API contracts implemented and tested

*Note: Full state transition design deferred to first business module (S01 - Identity & Access) per clarification resolution.*