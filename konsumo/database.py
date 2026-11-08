import os
import shutil
import sqlite3

SCHEMA = """
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
CREATE TABLE IF NOT EXISTS consumption (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 resource TEXT NOT NULL CHECK(resource IN ('electricity','water')),
 recorded_at TEXT NOT NULL,
 amount REAL NOT NULL CHECK(amount > 0),
 cost REAL,
 notes TEXT NOT NULL DEFAULT ''
);
"""

def connect(db_path):
    conn = sqlite3.connect(db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn

def init_db(db_path):
    target_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    # If a persistent path is configured, copy the previous local database
    # once when it is still available, before initializing the new location.
    configured_path = os.environ.get("KONSUMO_DB_PATH")
    legacy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "konsumo.sqlite3")
    if (configured_path and target_path == os.path.abspath(configured_path)
            and not os.path.exists(target_path) and os.path.isfile(legacy_path)
            and os.path.abspath(legacy_path) != target_path):
        shutil.copy2(legacy_path, target_path)
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(consumption)")}
        if "user_id" not in columns:
            # Upgrade databases created before account isolation was introduced.
            conn.execute("ALTER TABLE consumption ADD COLUMN user_id INTEGER REFERENCES users(id)")
            first_user = conn.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
            if first_user:
                conn.execute("UPDATE consumption SET user_id=? WHERE user_id IS NULL", (first_user["id"],))
        conn.execute("CREATE INDEX IF NOT EXISTS idx_consumption_user_resource_date ON consumption(user_id, resource, recorded_at)")
