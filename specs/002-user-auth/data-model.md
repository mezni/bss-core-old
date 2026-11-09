# Data Model: S01 Identity & Access

## Entities

### User

- **Description**: System entity representing an individual with authenticated access and assigned role(s).
- **Attributes**:
  - uid=1000(dali) gid=1000(dali) groups=1000(dali),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users),116(lpadmin),979(docker),981(vboxsf): Unique identifier (primary key)
  - : Unique login name within system scope
  - : Unique email address for communication and recovery
  - : Assigned access role determining permissions
  - : Current account status (active, locked, pending, archived)
  - : Timestamp of user account creation
  - : Timestamp of most recent successful authentication
  - : Count of consecutive failed authentication attempts
  - : Timestamp indicating when account lockout expires

- **Identity**: Uniquely identified by  within the system

- **Relationships**:
  - Has one associated  (many-to-one)
  - Owns authentication sessions and audit logs
  - Authentication events (logins, lockouts, password changes) are attributed to this entity

### Role

- **Description**: Named grouping of permissions that determines access scope for associated users.
- **Attributes**:
  - uid=1000(dali) gid=1000(dali) groups=1000(dali),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users),116(lpadmin),979(docker),981(vboxsf): Unique identifier (primary key)
  - : Unique role name within system scope
  - : Human-readable purpose of the role
  - : List of authorized actions and module access levels
  - : Timestamp of role creation
  - : Timestamp of last role permission modification

- **Identity**: Uniquely identified by  within system scope

- **Relationships**:
  - Has many associated  entities (one-to-many)
  - Permissions define access levels for: Identity & Access, Customer Management, Order Management, Shipment Management, Billing Management modules

- **Validation Rules** (from Functional Requirements):
  - Role name must be unique within system scope
  - Role description must not be empty
  - Role permissions must not be empty list

### Session

- **Description**: Active authentication session linking a verified user to system context.
- **Attributes**:
  - uid=1000(dali) gid=1000(dali) groups=1000(dali),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users),116(lpadmin),979(docker),981(vboxsf): Unique session identifier
  - : Reference to associated user
  - : Timestamp of session establishment
  - : Timestamp of session automatic expiration
  - : Timestamp of manual session termination
  - : Source IP address of authentication origin
  - : Client software identifier from authentication request

- **Identity**: Uniquely identified by  within system scope

- **Relationships**:
  - Belongs to exactly one  (many-to-one)
  - Session invalidation tracked via  timestamp

## Relationships

### User ↔ Role (Many-to-One)

- **User**: One user has exactly one role assigned
- **Role**: One role can be assigned to many users
- **Cardinality**: N Users → 1 Role
- **Deletion**: Role reassignment or deprecation deferred to module-level design

### User ↔ Session (One-to-Many)

- **User**: One user can have multiple active sessions (across devices)
- **Session**: Each session belongs to exactly one user
- **Cardinality**: 1 User → N Sessions
- **Deletion**: Session revocation on user account deactivation or lockout

### Module ↔ Role (Many-to-Many, through permissions)

- **Role**: Permissions map to module access levels across 5 modules
- **Module**: Identity & Access, Customer Management, Order Management, Shipment Management, Billing Management
- **Cardinality**: Roles have varying access levels per module

## Validation Rules (from Functional Requirements)

Per the functional requirements in the feature specification:

- **FR-001**: User must have authentication credentials and identity verified
- **FR-002**: Role-based access control must be consistent across the system
- **FR-005**: Database connection and session management must be configured for persistence
- **FR-006**: Database migration infrastructure must be version-controlled
- **FR-007**: Layer separation (Domain, Application, Infrastructure, Presentation) must be maintained
- **FR-008**: Module structure must organize business capabilities into bounded contexts
- **FR-009**: Unit and integration testing must be available from project start
- **FR-010**: Linting and formatting standards must be enforced automatically

## State Transitions (if applicable)

### User States

-  → User account is active and authentication permitted
-  → Account locked due to consecutive failed authentication attempts
-  → User account pending email verification or admin approval
-  → User account deactivated; data retained for audit purposes

### Role States

-  → Role is active and permissions enforceable
-  → Role is inactive; users with this role retain historical access but no new access granted

### Session States

-  → Session established, within expiration window, not revoked
-  → Session past expiration timestamp
-  → Session manually or programmatically terminated

*Full state transition design deferred to S01 - Identity & Access implementation per clarification resolution.*

---
