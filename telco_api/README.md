# Telecom CRM API

FastAPI + SQLAlchemy 2.0 + SQLite reference implementation for a telecom CRM backend:
subscribers, telecom lines, devices, invoices/payments, and usage CDRs with
JWT (OAuth2 password flow) + role-based access control (Admin vs CSR).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Seed the database (drops + recreates tables)
python -m app.seed

# Run the API
uvicorn app.main:app --reload
```

Interactive docs: http://127.0.0.1:8000/docs

## Seeded Credentials

10 system users, all with password `password`.

| Username | Role        |
|----------|-------------|
| user_1   | Admin       |
| user_2   | Admin       |
| user_3..user_10 | CSR |

```bash
curl -X POST http://127.0.0.1:8000/token \
  -d "username=user_1&password=password" \
  -H "Content-Type: application/x-www-form-urlencoded"

# Use the returned token:
curl http://127.0.0.1:8000/subscribers \
  -H "Authorization: Bearer <access_token>"
```

## Seeded Data Targets

| Domain | Target |
|--------|--------|
| System users | 10 (2 Admin, 8 CSR) |
| Subscribers | 10 (Prepaid/Postpaid) |
| Telecom lines | 1-2 active lines per subscriber |
| Devices | 10 mapped to subscribers + lines |
| Invoices | 50 across subscribers |
| Usage CDRs | 2,000 over the last 30 days |

## Endpoints

| Area | Routes |
|------|--------|
| Auth | `POST /token`, `GET/POST /users`, `GET /users/me`, `PATCH /users/{id}/status` |
| CRM | `GET/POST /subscribers`, `GET/PATCH/DELETE /subscribers/{id}`, `GET/POST /lines`, `GET /lines/{id}`, `PATCH /lines/{id}/status`, `GET /lines/stats/summary` |
| Devices | `GET/POST /devices`, `GET /devices/{id}`, `PATCH /devices/{id}/status`, `PATCH /devices/{id}/assign` |
| Billing | `GET/POST /invoices`, `GET /invoices/{id}`, `POST /invoices/{id}/payments`, `GET /payments`, `GET /billing/overview` |
| Usage | `GET/POST /usage`, `GET /usage/lines/{msisdn}/summary` |
| Admin | `POST /admin/generate-fake-data`, `GET /admin/health` |

## RBAC Model

- Any authenticated user (JWT) can read.
- Creating/updating business entities requires `CSR` or `Admin`.
- User management and `/admin/*` endpoints require `Admin`.

## Notes

- DB file: `./telecom.db` (see `app/database.py`).
- `POST /invoices/{id}/payments` auto-marks an invoice `Paid` once aggregated
  payments cover the invoice amount.
- `POST /usage` accumulates `Data` sessions into the line's `data_usage_gb`.
- Change `SECRET_KEY` in `app/auth.py` for any real deployment.