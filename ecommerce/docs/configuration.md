# Configuration — Fake E-Commerce Server

> **Status:** Draft
> **Authority:** `.specify/memory/constitution.md` v1.1.0, *Security and Observability*

Configuration is **externalized**. Environment variables carry environment-specific settings, so
the same image behaves correctly in development, test, and production without code changes.

Secrets MUST NOT be committed. `.env.example` documents every variable without containing real
secrets.

---

## 1. Variables

| Variable | Type | Default | Used by | Purpose |
|---|---|---|---|---|
| `DATABASE_URL` | str | `sqlite+aiosqlite:///./data/ecommerce.db` | app, migrations, generator | SQLAlchemy DSN |
| `APP_ENV` | enum | `development` | all | `development` \| `test` \| `production` |
| `LOG_LEVEL` | enum | `INFO` | app | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` \| `CRITICAL` |
| `LOG_FORMAT` | enum | `text` | app | `text` (dev) \| `json` (prod) |
| `RANDOM_SEED` | int | `42` | generator, tests | Default seed for reproducible data |
| `FAKE_FAILURE_RATE` | float | `0.0` | failure sim | Probability of **randomized** failure injection, `0.0`–`1.0`. `0.0` disables it |
| `FAKE_LATENCY_MS` | int | `0` | failure sim | Artificial latency added per request |
| `FAKE_FAILURE_ENABLED` | bool | `false` | failure sim | Master switch for all failure simulation |
| `FAKE_CLOCK` | str | *(unset)* | app, tests | Fixed ISO-8601 instant for deterministic time |
| `AUTH_ENABLED` | bool | `true` | API | Enforce authentication/authorization |
| `CORS_ORIGINS` | list | `[]` | app | Allowed origins |
| `API_V1_PREFIX` | str | `/api/v1` | app | Route prefix |
| `SEED_PROFILE` | enum | `development` | generator | Default profile when `--profile` is omitted |

Settings are read once at startup via `pydantic-settings` in
`src/ecommerce/config/settings.py`. Invalid values fail fast at startup rather than at first use.

### 1.1 The critical ones

```bash
DATABASE_URL=sqlite+aiosqlite:///./data/ecommerce.db
APP_ENV=development
LOG_LEVEL=INFO
RANDOM_SEED=42
FAKE_FAILURE_RATE=0.0
FAKE_LATENCY_MS=0
```

---

## 2. Environment Differences

### 2.1 `development`

| Setting | Value | Rationale |
|---|---|---|
| `APP_ENV` | `development` | |
| `LOG_LEVEL` | `DEBUG` | Verbose; shows SQLAlchemy queries if enabled |
| `LOG_FORMAT` | `text` | Human-readable |
| `FAKE_FAILURE_ENABLED` | `false` | Never surprise a developer mid-task |
| `FAKE_FAILURE_RATE` | `0.0` | No random failures |
| `FAKE_LATENCY_MS` | `0` | No artificial slowness |
| `AUTH_ENABLED` | `true` | Realistic boundary, easy fake credentials |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/ecommerce.db` | Disposable dev file |
| Reload | enabled | `uvicorn --reload` |
| Docs | `/docs` enabled | Interactive exploration |

The dev database is disposable. If it is corrupted, delete it and re-run `make migrate && make seed`.

### 2.2 `test`

| Setting | Value | Rationale |
|---|---|---|
| `APP_ENV` | `test` | |
| `LOG_LEVEL` | `WARNING` | Keeps test output readable |
| `LOG_FORMAT` | `text` | |
| `FAKE_FAILURE_ENABLED` | `false` | Default off; tests opt in explicitly |
| `FAKE_FAILURE_RATE` | `0.0` | Determinism over realism |
| `FAKE_LATENCY_MS` | `0` | No sleeping in tests |
| `FAKE_CLOCK` | fixed instant | Deterministic timestamps |
| `AUTH_ENABLED` | `true` | Auth paths are tested explicitly |
| `DATABASE_URL` | dedicated test DB | **Never** the dev database |
| `RANDOM_SEED` | fixed (e.g. `42`) | Reproducible fixtures |

`APP_ENV=test` MUST NOT read ambient developer configuration — otherwise a test run can silently
target a developer's real database.

```bash
APP_ENV=test
DATABASE_URL=sqlite+aiosqlite:///./.tmp/test.db
RANDOM_SEED=42
FAKE_CLOCK=2026-01-01T00:00:00Z
```

### 2.3 `production`

| Setting | Value | Rationale |
|---|---|---|
| `APP_ENV` | `production` | |
| `LOG_LEVEL` | `INFO` | No debug noise in production logs |
| `LOG_FORMAT` | `json` | Machine-parseable for aggregation |
| `FAKE_FAILURE_ENABLED` | `false` | Never inject failures in production |
| `FAKE_FAILURE_RATE` | `0.0` | |
| `FAKE_LATENCY_MS` | `0` | |
| `AUTH_ENABLED` | `true` | Mandatory |
| `DATABASE_URL` | from secret/env | Real DSN, never committed |
| Docs | disabled | `/docs` and `/openapi.json` off |

> This project is a **fake** server; "production" here means *production-shaped configuration for
> realistic deployments and client testing*, not a real commercial deployment.

Hard guards: when `APP_ENV=production`, the application refuses to start if
`FAKE_FAILURE_ENABLED=true` or `FAKE_FAILURE_RATE > 0`. Simulated failure is a test affordance
and MUST NOT leak into a production-shaped environment.

---

## 3. `.env.example`

Committed; contains **no real secrets**:

```bash
# --- Application ---
APP_ENV=development
LOG_LEVEL=INFO
LOG_FORMAT=text
API_V1_PREFIX=/api/v1
CORS_ORIGINS=[]

# --- Database ---
DATABASE_URL=sqlite+aiosqlite:///./data/ecommerce.db

# --- Determinism ---
RANDOM_SEED=42
# FAKE_CLOCK=2026-01-01T00:00:00Z

# --- Failure simulation (dev/test only) ---
FAKE_FAILURE_ENABLED=false
FAKE_FAILURE_RATE=0.0
FAKE_LATENCY_MS=0

# --- Auth ---
AUTH_ENABLED=true
# AUTH_FAKE_TOKEN_SECRET=change-me-not-a-real-secret

# --- Generator ---
SEED_PROFILE=development
```

Rules:

* `.env` is **git-ignored**; `.env.example` is committed.
* `.env` MUST NOT contain real secrets, and no real secret belongs in this project at all — all
  credentials are synthetic by design.
* Values shown in `.env.example` are safe placeholders.

---

## 4. Precedence

```text
CLI flag  >  environment variable  >  .env file  >  documented default
```

```bash
uv run python -m ecommerce.seed --seed 7
```

`--seed 7` beats `RANDOM_SEED=42` from the environment. The effective value is always echoed in
the generator summary so a run is reproducible from recorded output alone.

---

## 5. Failure Simulation Defaults

Failure simulation is controlled by **four** variables, and the interaction matters:

| `FAKE_FAILURE_ENABLED` | `FAKE_FAILURE_RATE` | Behavior |
|---|---|---|
| `false` | any | All simulation off. `X-Fake-Failure` is **ignored**. |
| `true` | `0.0` | Only **deterministic**, explicitly requested failures via `X-Fake-Failure`. Recommended default even when enabled. |
| `true` | `> 0.0` | Adds **randomized** injection for resilience testing. |

Deterministic-first is deliberate: a test that asserts "this request fails" must never lose a
coin flip. Randomized injection is for soak/resilience testing only, and is independently
controlled from the deterministic path. Full behavior: `docs/failure-simulation.md`.

---

## 6. Validation at Startup

| Rule | Failure mode |
|---|---|
| `APP_ENV` in the allowed set | Startup error listing valid values |
| `LOG_LEVEL` in the allowed set | Startup error |
| `FAKE_FAILURE_RATE` in `[0.0, 1.0]` | Startup error |
| `FAKE_LATENCY_MS >= 0` | Startup error |
| `DATABASE_URL` parses as a SQLAlchemy URL | Startup error |
| `APP_ENV=production` + failure simulation enabled | **Refuse to start** |
| `APP_ENV=test` + dev database URL | Refuse to start (protects dev data) |

Failing at startup is always preferable to failing on the first request that happens to need the
value.

---

## 7. Adding a Variable

1. Add the field to `src/ecommerce/config/settings.py` with a type and a documented default.
2. Document it in this file **and** in `.env.example`.
3. Note any environment-specific difference in §2.
4. If it affects the generator, document it in `docs/generator.md`.
5. If it affects failure simulation, document it in `docs/failure-simulation.md` and update the
   table in §5.

Configuration that changes behavior MUST be documented. Configuration is part of the contract, not
an implementation detail.
