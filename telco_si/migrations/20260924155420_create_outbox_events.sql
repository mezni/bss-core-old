CREATE TABLE outbox_events (
    id TEXT PRIMARY KEY NOT NULL,

    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,

    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,

    occurred_at TEXT NOT NULL,
    created_at TEXT NOT NULL,

    published_at TEXT NULL,

    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT NULL
);

CREATE INDEX idx_outbox_events_unpublished
    ON outbox_events(published_at, created_at);