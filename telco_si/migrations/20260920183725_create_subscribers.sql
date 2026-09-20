CREATE TABLE subscribers (
    id TEXT PRIMARY KEY NOT NULL,
    account_number TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    balance_cents INTEGER NOT NULL DEFAULT 0,
    plan_id TEXT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    CONSTRAINT subscribers_status_check
        CHECK (status IN ('active', 'suspended', 'terminated')),

    CONSTRAINT subscribers_balance_check
        CHECK (balance_cents >= 0)
);

CREATE INDEX idx_subscribers_status
    ON subscribers(status);
