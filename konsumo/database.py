import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS consumption (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 resource TEXT NOT NULL CHECK(resource IN ('electricity','water')),
 recorded_at TEXT NOT NULL,
 amount REAL NOT NULL CHECK(amount > 0),
 cost REAL,
 notes TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_consumption_resource_date ON consumption(resource, recorded_at);
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 email TEXT NOT NULL UNIQUE COLLATE NOCASE,
 password_salt TEXT NOT NULL,
 password_hash TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
 token TEXT PRIMARY KEY,
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON sessions(expires_at);
"""

def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
