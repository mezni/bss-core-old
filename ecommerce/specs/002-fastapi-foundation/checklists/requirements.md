# Specification Quality Checklist: FastAPI Foundation

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-26
**Feature**: [spec.md](../spec.md)

**Validation run 1 — 2026-09-26. Result: 16/16 pass, 0 fail, 0 clarifications required
after resolution.** The run below documents each item's evidence.

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

### Validation run 3 — 2026-09-26 (planning-time correction). Result: 16/16 pass, 0 marker changes

**No item changed state.** One sentence was corrected, prompted by
`docs/configuration.md` §11 while resolving a design question during `/speckit.plan`.

*Requirements are testable and unambiguous* was **strengthened**. FR-004 had been given
the sentence "a consumer who knows the path can still retrieve the schema", carried over
from the configuration document. That sentence is not implementable: `/openapi.json` is
the only URL the schema is served from, and the document names no second path, so the
sentence contradicted the same document's claim that the switch hides `/openapi.json`.
The clause now states the switches are not a security boundary — which is the document's
actual intent — and drops the retrieval claim. Rationale is recorded as decision D-05 in
`research.md`, and the configuration document is queued for a wording fix so the
published contract stops contradicting itself.

*Acceptance criteria per requirement* is unaffected: the change alters how a requirement
is worded, not what must be observed, and FR-004's observation (Story 2 AS 5) still
covers it.

---

## Notes

- Items marked incomplete require spec updates before `/speckit.clarify` or
  `/speckit.plan`.

### Validation run 2 — 2026-09-26 (post-clarification). Result: 16/16 pass, 0 fail, 0 marker changes

**Before: 16/16 — after: 16/16.** No item changed state: no regressions, and nothing
newly passed. Clarification did not weaken the specification; it strengthened three
requirements and removed one that could not be satisfied. Marker state was deliberately
left untouched, and the evidence below was corrected where it had gone stale.

**One defect found and corrected without asking.** Cross-checking the spec against
`docs/API.md` §25.1 and the endpoint table in `docs/configuration.md` §10 showed the spec
contradicted the authoritative contract: it required the liveness check to report the
application version. The published payload is `{"status": "ok"}` with no version, and
the version belongs on `/ready`, which §25.2 marks planned and not required. The reason
given is that a versioned or version-bearing liveness probe is the wrong place for it.
Corrected in FR-002, Story 1 AS 3, and the *Liveness report* entity. This was not raised
as a question because the published documents settle it unambiguously — a question would
have invited the user to overturn a decision that is already recorded elsewhere.

**Three questions asked, three answered, all integrated** (see *Clarifications* in the
spec). Effects on the items:

- *Requirements are testable and unambiguous* — **strengthened**. FR-005 previously said
  only that the identity "MUST appear in the machine-readable description", which left
  the published version's origin unspecified; two candidate sources existed and either
  could have been implemented. The source is now fixed and the absence of drift is a
  stated, testable outcome (SC-011) rather than an unstated hope.
- *Success criteria are measurable* / *technology-agnostic* — **strengthened**. SC-011
  adds a measurable outcome in outcome terms; it names neither the setting nor the tool.
- *All acceptance scenarios are defined* — **strengthened**. Story 2 gained a fifth
  scenario covering a disabled description, which is the case the newly honoured switches
  create and which no scenario previously covered.
- *Edge cases are identified* — **strengthened**. Three cases added for failure modes the
  switches and configurable prefix introduce: a non-boolean switch value, an empty or
  conflicting prefix, and a disabled description.
- *Dependencies and assumptions* — **strengthened**. Cross-origin access is now named as
  an explicit exclusion, and the dependency on the not-yet-present configuration template
  is recorded rather than assumed satisfied. Doing so also exposed a self-contradiction:
  the template's existence was asserted in one assumption while another recorded its
  absence. The unsupported claim was removed.
- *Acceptance criteria per requirement* — **corrected, not changed**. The coverage table
  above listed Story 2 as AS 1–4 and omitted the new SC-011 row; both were stale after
  the edits and have been fixed. The item's pass state is unchanged.

**One nuance recorded rather than hidden.** The spec now references two published
configuration settings by name inside the *Clarifications* record, and refers to them
functionally ("a documented setting", "the project's documented first-version value")
everywhere in the requirements themselves. This is judged compliant for the *No
implementation details* and *No implementation details leak* items: the names come from
`docs/configuration.md`, which the constitution classifies as a requirements document, and
a requirement that reads a setting without naming it is still testable. The names appear
only as the record of a question the user was asked.

**Requirement count changed**: 18 functional requirements (unchanged in number; FR-002,
FR-004, FR-005, FR-006, and FR-018 amended in place rather than renumbered, to avoid
churning every cross-reference), 11 success criteria (SC-011 added), 6 key entities
(*Description switch* added), 11 edge cases, 13 assumptions.

### Validation run 1 — evidence

**Draft state before this run.** The first draft carried two
`[NEEDS CLARIFICATION]` markers and was rejected on review. Both were defects in the
draft, not genuine ambiguities in the feature:

- *Authentication method.* Raised as FR-006. Invalid: `docs/plan.md` §7 (Phase 1)
  contains no authentication objective, and §18 places authentication in Phase 12. A
  clarification was raised for a decision this feature does not make. **Resolved by
  removal.** FR-006/FR-007 are deleted; the requirement they stood for does not exist in
  this phase. The clarification prompt was answered *OAuth2*, and that answer is recorded
  in *Assumptions* as a forward-looking decision for the later authentication feature, so
  the answer is preserved without importing a Phase 12 requirement into Phase 1.
- *Data retention period.* Raised as FR-007. Invalid: nothing in `docs/plan.md` §7
  creates persistent user data, so no retention period is observable in this phase.
  **Resolved by removal**, and the exclusion is stated in *Assumptions* so the omission
  is visible rather than silent.

No clarification was left unresolved, so no question remains for the user.

### Content Quality

- *No implementation details* — pass. No requirement or success criterion names a
  language, framework, database, migration tool, test runner, file path, endpoint path,
  or command. Verified by scan: the only occurrences of the framework name are in the
  document title, the branch slug, and the *Input* line that quotes `docs/plan.md` §7's
  own phase heading. The stack is inherited as a constraint from the constitution and
  `docs/plan.md` §2 and is named only in *Assumptions*, as the prior feature's checklist
  also did.
- *Focused on user value* — pass. All three stories are developer- or consumer-visible
  outcomes: reach a running server, obtain the API surface without reading source, and
  add a real endpoint later without renegotiating the foundation. FR-016, FR-017, and
  FR-018 are the exception and are retained deliberately: they are constraints on what
  this phase must *not* deliver, made testable because the constitution makes them
  binding (Principle V, Architecture, Development Workflow).
- *Non-technical stakeholders* — pass, with the caveat recorded rather than hidden. The
  audience is necessarily technical, so the spec is written in outcome terms — "reports
  the service is operational", "a machine-readable description of the API surface" — and
  a stakeholder can review scope, edge cases, and every success criterion without
  reading code. Endpoints are referred to by role (liveness check, interactive
  description, machine-readable description, versioned namespace) rather than by path.
- *Mandatory sections* — pass. *User Scenarios & Testing*, *Requirements* (Functional
  Requirements, Key Entities), *Success Criteria*, and *Assumptions* are all populated.
  Zero template placeholders and zero `ACTION REQUIRED` comments remain, verified by
  scan.

### Requirement Completeness

- *Clarification markers* — pass. Zero remain after the two draft defects above were
  removed. The limit of three was never reached.
- *Testable and unambiguous* — pass. Each of FR-001…FR-018 names an observable: a
  command's exit status, a response's content, a file's absence or presence, a
  repository scan, or a structural property. The negative requirements are phrased so an
  observer can confirm compliance: "MUST NOT expose an internal exception, stack trace,
  or file system path" is checkable by inspecting responses; "MUST NOT introduce a
  service boundary, message broker, background worker, event store, or command/query
  separation" is checkable by inspecting the dependency graph.
- *Measurable success criteria* — pass. All ten carry a number and an observation method:
  percentage of clean-checkout starts reaching a running server (SC-001), percentage of
  repeated liveness successes (SC-002), percentage of runs serving both descriptions and
  of automated checks parsing the machine-readable form (SC-003), percentage of unknown
  paths returning the standard error structure with a count of leaked internals (SC-004),
  injection-detection rate with a non-zero-exit clause (SC-005), percentage of automated
  checks actually executing, with zero-collection treated as failure (SC-006), a
  wall-clock bound in seconds (SC-007), documentation coverage (SC-008), percentage of
  degraded-configuration cases still reaching a running server (SC-009), and a
  convenience-layer equivalence rate (SC-010).
- *Technology-agnostic criteria* — pass. No SC names a framework, language, database,
  or tool. Where the prior feature used the phrase "interpreter baseline", this one
  avoids naming the runtime at all: SC-001 is expressed as "the two documented
  commands", SC-003 as "the machine-readable form", SC-005 as "the documented
  verification command".
- *Acceptance scenarios* — pass. Three prioritized stories with 4, 4, and 3 scenarios
  respectively — 11 total, each in Given/When/Then form, each independently observable,
  and each phrased without naming a path or a tool.
- *Edge cases* — pass. Ten cases, each chosen because it is a realistic failure for this
  phase and each grounded in a requirement rather than invented: absent configuration
  (FR-010), empty or partial configuration (FR-010), occupied port and double start
  (FR-014), wrong working directory (FR-014), unknown path (FR-008, FR-009), liveness
  independence from a degraded subsystem (FR-003), invalid configuration value
  (FR-011), and failed reload leaving the previous process available. The liveness
  versus readiness distinction is recorded as a deferred concern rather than left
  implicit.
- *Scope* — pass. Bounded explicitly by FR-018, which enumerates both what this feature
  delivers and what it excludes: business capabilities, persistence, migrations,
  generated data, failure simulation, authentication, and request instrumentation.
  *Assumptions* records the exclusions a reader would otherwise have to infer,
  including readiness endpoints and structured logging.
- *Dependencies and assumptions* — pass. Eleven assumptions, each covering a decision
  the description left open with the reason it was resolved that way. Two of them
  (authentication, retention) exist specifically so that questions raised and then
  removed from scope stay traceable.

### Feature Readiness

- *Acceptance criteria per requirement* — pass. Coverage is complete:

  | Requirement | Covered by |
  |---|---|
  | FR-001, FR-002, FR-003, FR-013, FR-014 | Story 1 (AS 1–4) |
  | FR-004, FR-005, FR-006 | Story 2 (AS 1–5) |
  | FR-007, FR-008, FR-009 | Story 3 (AS 1–3) |
  | FR-010, FR-011, FR-012 | Edge cases; SC-009 |
  | FR-015, FR-016, FR-017, FR-018 | SC-005, SC-006, SC-010; constitution gates |
  | FR-005 version equality clause | SC-011 |

  No requirement is left without an observation that can fail.
- *Primary flows covered* — pass. The three stories are the complete Phase 1 path: start
  and verify, describe, extend. P1 alone is a viable deliverable with observable value,
  and P2 and P3 each stand on their own, satisfying the independent-testability rule.
- *Success criteria reachable* — pass. Every SC is satisfiable by work in scope and
  verifiable without reading the implementation. SC-008 is measured against the
  entry-point document alone, as the prior feature measured its equivalent.
- *No implementation leakage* — pass. *Key Entities* describes concepts and their
  attributes — application identity, liveness report, route, versioned namespace, error
  report — and names no tables, classes, modules, or endpoints.

### Follow-ups raised, not resolved here

Recorded per constitution Principle III and Governance, rather than silently decided:

1. **Feature numbering.** This is feature `002`. The constitution's *Speckit Development
   Process* block enumerates `001-foundation` … `011-observability`, and the repository
   contains `001-project-foundation` rather than `001-foundation`. The same divergence
   `001-project-foundation` recorded as a deferred conflict is therefore still open, and
   this feature does not resolve it. A later decision must either amend the constitution
   block or rename the directory.
2. **Roadmap table.** `specs/README.md` still presents the removed placeholder slugs as
   existing directories. Not this feature's scope to change; recorded so it stays
   visible.
3. **Clarification carried forward.** The OAuth2 answer given during this run is recorded
   in *Assumptions* and constrains nothing here. The authentication feature should treat
   it as a prior decision rather than reopening the question.
