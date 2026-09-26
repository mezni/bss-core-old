# Contract: Configuration Template Format

**Feature**: `001-project-foundation` | **Status**: binding | **Date**: 2026-09-26

`docs/configuration.md` §42 is the upstream authority for *which* variables exist and what
they mean. This contract defines only the *file format* of `.env.example` and the
*coverage rule* that keeps the file and the reference in agreement. The variables are not
restated here, so the two documents cannot drift.

Governs: FR-009, FR-010, FR-011, FR-012, SC-007, SC-008.

---

## 1. Coverage rule

`.env.example` MUST contain an entry for **every** variable in `docs/configuration.md` §42
— all 30, including the two marked *Reserved* and the one marked sensitive. This is
clarification 3: the template is exhaustive, and availability is expressed per setting
rather than by omission.

`scripts/check_config_template.py` enforces the rule. It fails when the two key sets
differ in either direction, when an entry lacks a status token, or when a default
disagrees with the reference.

## 2. Entry format

One variable per line, in the reference's order:

```text
VARIABLE_NAME=<default>  # status: <honoured | planned (<phase>)> — <purpose>. <validation rule, if any>
```

Requirements per entry:

| Part | Rule |
|---|---|
| Name | Upper snake case; byte-identical to the reference key. |
| Assignment | `NAME=value`. No `export`, no quotes unless the value contains a space. |
| Default | Byte-identical to the reference default. An unset default is written commented-out with `*(unset)*` noted, never as an empty value. |
| Status token | Required. `# status: honoured` or `# status: planned (<phase>)`. A missing token is non-conforming. |
| Purpose | One line, effect not mechanism. |
| Validation rule | Required for constrained values (enum membership, numeric range, format). Omitted for unconstrained types. |

### 2.1 Sensitive settings

A setting marked sensitive in the reference ships **commented out**, with a synthetic
placeholder value clearly marked as synthetic. It MUST NOT carry a real credential, and
the string `AUTH_FAKE_TOKEN_SECRET=` MUST NOT appear uncommented with a non-empty value
(FR-010, SC-008).

### 2.2 Grouping

Entries MAY be grouped under comment headings by concern (application, server, database,
observability, generator, failure simulation, auth). Grouping is cosmetic and MUST NOT
change the coverage rule or the entry format.

## 3. The status token vocabulary

One vocabulary, used here and in `README.md` for commands (clarifications 1 and 3 both
require an explicit availability marker; they must not produce two different conventions —
research D10):

| Token | Meaning |
|---|---|
| `honoured` | Read by the code in this phase. |
| `planned (<phase>)` | Documented but not yet read. `<phase>` names the phase that will read it. |

`planned` is not "maybe" and not "coming soon". It names a phase. A setting with no token
is a defect, not a default.

## 4. Relationship to the local configuration file

- `.env.example` is committed. `.env` is ignored (FR-013) and MUST NOT be committed
  (SC-008).
- The local file is a copy of the template with values changed. Removing a line from the
  local file returns that setting to its documented default (FR-012).
- An unrecognised entry in the local file MUST NOT break startup. Defaults still apply
  and the unknown entry is ignored (spec edge case).
- No real secret, credential, personal datum, or machine-specific absolute path appears in
  the template (FR-010).

## 5. Reading the template in this phase

Phase 0 ships the template and the check. It does **not** ship the runtime settings module
— configuration *loading* and start-up validation belong to Phases 1–2 of this feature.
Consequently every variable is `planned` in this phase except any that a Phase 0 check
genuinely reads, and the check script is the only such reader.

This is the honest consequence of clarification 3: the template is complete and marked,
not partially omitted. A contributor reading it learns the full configuration surface on
day one and can see exactly which settings take effect today.

## 6. Change rules

- Adding a variable to `docs/configuration.md` §42 without adding it to `.env.example`
  fails `make check`. So does the reverse.
- Moving a setting from `planned (<phase>)` to `honoured` requires the code that reads it
  in the same change. A setting marked `honoured` with no reader is a defect.
- Changing the entry format or the status token is a breaking change: recorded in
  `CHANGELOG.md` in the same change (FR-016).
- The five items in `docs/configuration.md` §42.1 — *deliberately not configurable* — are
  NOT variables and MUST NOT appear in the template. They are a different category, and
  their absence from the file is correct, not a coverage gap.
