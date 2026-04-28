CREATE TABLE IF NOT EXISTS identity_links (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR NOT NULL,
    linked_email  VARCHAR NOT NULL,
    last_updated  DATE NOT NULL,
    UNIQUE (email, linked_email)
);

CREATE TABLE IF NOT EXISTS login_events (
    id            SERIAL,
    email         VARCHAR NOT NULL,
    ts            TIMESTAMP NOT NULL ,
    ip            VARCHAR NOT NULL,
    inserted_date DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (id, ts)
) PARTITION BY RANGE (ts);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_login_events_ip_ts      ON login_events (ip, ts);
CREATE INDEX IF NOT EXISTS idx_login_events_email_ts   ON login_events (email, ts);
CREATE INDEX IF NOT EXISTS idx_login_events_inserted   ON login_events (inserted_date);

CREATE INDEX IF NOT EXISTS idx_identity_links_email        ON identity_links (email);
CREATE INDEX IF NOT EXISTS idx_identity_links_linked_email ON identity_links (linked_email);
CREATE INDEX IF NOT EXISTS idx_identity_links_last_updated ON identity_links (last_updated);