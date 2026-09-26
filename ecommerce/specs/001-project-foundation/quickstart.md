# Quickstart: Validating Project Foundation (Phase 0)

**Feature**: `001-project-foundation` | **Date**: 2026-09-26

A runnable guide to proving this feature works end to end. Every scenario maps to a
success criterion in [spec.md](spec.md), so a failure here is a failure of a named
criterion rather than a vague breakage.

This is a validation guide, not an implementation guide. It contains no application code,
no model definitions, and no test bodies — those belong in `tasks.md` and the
implementation phase. Details of the two command surfaces live in
[contracts/developer-commands.md](contracts/developer-commands.md) and
[contracts/config-template.md](contracts/config-template.md); the record shapes live in
[data-model.md](data-model.md).

---

## Prerequisites

- A supported CPython **3.12** available to the project's dependency manager. Nothing
  else needs to be installed: the project installs its own tooling.
- Network access for the first install.
- Version control, for the hygiene checks that inspect tracked files.
- About ten minutes. SC-001 budgets two commands and under ten minutes.

Run every command below **from the project root**. Running from elsewhere is a defined
failure, not a convenience.

---

## Scenario 1 — The two-command path (SC-001, SC-002)

The primary acceptance path. On a clean checkout:

```bash
uv sync
make check
```

| Expect | Signal |
|---|---|
| `uv sync` succeeds | exit 0; installed versions match the committed `uv.lock` |
| `make check` succeeds | exit 0 |
| Total commands | exactly 2 |
| Elapsed | under 10 minutes |

Repeat `uv sync` immediately. The second run MUST produce the same outcome with no
unexpected upgrades (spec edge case: warm-cache and repeat installs).

```bash
uv sync
```

## Scenario 2 — The package is importable without activation (FR-007)

```bash
uv run python -c "import ecommerce; print(ecommerce.__version__)"
```

Expect a version string and exit 0 — with no `PYTHONPATH`, no `pip install -e .`, and no
`.venv` activation. Confirm the resolution points inside the source tree:

```bash
uv run python -c "import ecommerce; print(ecommerce.__file__)"
```

## Scenario 3 — The suite runs and is not empty (FR-020, SC-005)

```bash
uv run pytest
uv run pytest tests/unit
```

Expect a non-zero-collection run to be impossible: the suite MUST report success by
actually executing at least one check, never by collecting nothing. Confirm the count is
greater than zero in the output.

## Scenario 4 — All three test areas are present on a fresh clone (FR-021, SC-012)

```bash
git clean -xdn | head -20
ls tests/unit tests/integration tests/api
```

Expect all three areas present, each with at least one tracked file. The dry-run clean
output is the check that matters: nothing untracked may be required for the layout to
exist, because an untracked file does not survive a clone.

## Scenario 5 — Checks actually fail when they should (FR-019, SC-006)

Each of these MUST report failure with a non-zero exit status. Revert each change
immediately after confirming the failure.

| Injected violation | Command | Expect |
|---|---|---|
| Formatting drift | `make format` then `make check` | non-zero, names the file |
| A failing test | `uv run pytest` | non-zero, names the test |
| An unused dependency | add a dependency to `pyproject.toml` with no import and no `later phase (<n>)` record | `make check` non-zero, names the dependency |
| A staged local configuration file | `git add -f .env` | `make check` non-zero, names the path |
| A secret-shaped value | set a tracked file's `*_TOKEN` to a non-empty value | `make check` non-zero, names the file |

## Scenario 6 — The configuration template is complete (FR-009, SC-007)

```bash
make check
```

Expect the configuration check to pass, having compared `.env.example` against
`docs/configuration.md` §42. To see it working, delete one entry from `.env.example` and
re-run: it MUST fail and name the missing key. Restore the file afterwards.

Then confirm by inspection that:

- all 30 variables are present;
- every entry carries a status token;
- the sensitive setting is commented out with a synthetic value;
- no entry holds a real credential or a machine-specific absolute path (FR-010).

## Scenario 7 — Defaults hold with no local configuration file (FR-012)

```bash
rm -f .env
make check
```

Expect success. Removing the local configuration file must not break anything, because
every setting has a documented default. Restore `.env` if you had one.

## Scenario 8 — Ignore rules and secret hygiene (FR-013, FR-014, SC-008)

```bash
printf 'DATABASE_URL=sqlite:///./data/x.db\n' > .env
git add -f .env
make check
```

Expect failure naming `.env`. Then confirm the ignore rules themselves:

```bash
git check-ignore -v .env data/ .venv/ 2>/dev/null
```

Expect each ignored path to be attributed to a rule in `.gitignore`. Unstage and delete
the file afterwards.

## Scenario 9 — The interpreter rule (FR-002, SC-011)

```bash
uv run python --version
```

Expect 3.12.x, pinned by `.python-version`. Then confirm the floor is declared rather
than assumed:

```bash
grep requires-python pyproject.toml
cat .python-version
```

Expect `>=3.12` and `3.12`. Optionally run `uv run --python 3.11 python --version` to
observe the rejection path; expect a message naming the required version rather than a
downstream error.

## Scenario 10 — Documentation honesty (FR-015, FR-010, SC-010)

Read `README.md` alone, as a first-time contributor would. You should be able to state:

1. the project's purpose;
2. its supported stack;
3. the install, run, migrate, seed, and test commands;
4. **which of those work today** — each carries a status token.

A command in the *Target workflow* section with no status token is a defect.

## Scenario 11 — Convenience commands add nothing (FR-017, SC-009)

Pick any available target and run its plain command directly. The result MUST be
identical to running the target:

```bash
uv run pytest          # same as: make test
uv run ruff check .    # same as: make lint
```

No step may exist only inside the convenience layer.

---

## Expected results summary

| # | Scenario | Criteria |
|---|---|---|
| 1 | Two-command path | SC-001, SC-002 |
| 2 | Importable without activation | FR-007 |
| 3 | Suite runs, not empty | FR-020, SC-005 |
| 4 | Three test areas on a fresh clone | FR-021, SC-012 |
| 5 | Checks fail when they should | FR-019, SC-006 |
| 6 | Configuration template complete | FR-009, SC-007 |
| 7 | Defaults hold with no local file | FR-012 |
| 8 | Ignore rules and secret hygiene | FR-013, FR-014, SC-008 |
| 9 | Interpreter rule | FR-002, SC-011 |
| 10 | Documentation honesty | FR-015, FR-010, SC-010 |
| 11 | Convenience commands add nothing | FR-017, SC-009 |

**A green run of all eleven is the definition of done for this feature.** A phase that
merely installs successfully has not met `docs/plan.md` §6, which requires both that the
project install and that the test environment execute successfully.

## What this guide does not cover

Deliberately, because they belong to later phases of this feature or to later features:
starting a server, `GET /health`, applying migrations, generating fake data, failure
simulation, authentication, and observability. If a command in `README.md` is documented
for one of those, it carries a `planned` marker and is not expected to run.
