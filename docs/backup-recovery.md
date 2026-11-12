# SQLite Backup and Recovery

**Scope:** S07 MVP operational procedure (S07-10).

The MVP uses a single SQLite database (`db/bss_core.db` by default, or the
path in `BSS_DATABASE_URL`). Back up with SQLite's online backup mechanism so a
running application can be captured consistently without stopping writes.

## Backup (VACUUM INTO)

```bash
# Produces a compact, consistent copy; fails if the target exists.
uv run python - <<'PY'
import sqlite3
from pathlib import Path

source = Path("db/bss_core.db")
target = Path("db/backups") / "bss_core-backup.db"
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists():
    raise SystemExit(f"refusing to overwrite {target}")

with sqlite3.connect(source) as connection:
    connection.execute("VACUUM INTO ?", (str(target),))
print(f"backup written to {target}")
PY
```

`VACUUM INTO` writes a defragmented copy and is safe while the application is
running. Store backups outside the application directory and protect them as
financial data.

## Recovery

1. Stop the backend (`uvicorn`) and any Streamlit client.
2. Keep the failed database for forensics:
   `mv db/bss_core.db db/bss_core.db.failed-$(date +%Y%m%d%H%M%S)`.
3. Restore the most recent verified backup: `cp db/backups/bss_core-backup.db db/bss_core.db`.
4. Verify integrity and schema version:

   ```bash
   uv run python -c "import sqlite3; print(sqlite3.connect('db/bss_core.db').execute('PRAGMA integrity_check').fetchone())"
   uv run alembic current
   ```

5. Restart the backend and run the health check:
   `curl -fsS http://localhost:8000/health`.

## Verification cadence

Verify the procedure once per release using quickstart Scenario 10: create a
known record, take a `VACUUM INTO` backup, delete the record, restore the
backup, and confirm the record is present. Record the date and result in the
release sign-off notes.
