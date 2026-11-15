"""SQLite for local development; PostgreSQL for serverless deployments."""
import os, shutil, sqlite3, threading

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE, password_salt TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, expires_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON sessions(expires_at);
CREATE TABLE IF NOT EXISTS consumption (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, resource TEXT NOT NULL CHECK(resource IN ('electricity','water')), recorded_at TEXT NOT NULL, amount REAL NOT NULL CHECK(amount > 0), cost REAL, notes TEXT NOT NULL DEFAULT '');
"""
PG_SCHEMA = (
"CREATE TABLE IF NOT EXISTS users (id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_salt TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
"CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE, expires_at TEXT NOT NULL)",
"CREATE TABLE IF NOT EXISTS consumption (id BIGSERIAL PRIMARY KEY, user_id BIGINT REFERENCES users(id) ON DELETE CASCADE, resource TEXT NOT NULL CHECK(resource IN ('electricity','water')), recorded_at TEXT NOT NULL, amount DOUBLE PRECISION NOT NULL CHECK(amount > 0), cost DOUBLE PRECISION, notes TEXT NOT NULL DEFAULT '')",
"CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON sessions(expires_at)",
"CREATE INDEX IF NOT EXISTS idx_consumption_user_resource_date ON consumption(user_id, resource, recorded_at)",
)
def _pg_url(path=None):
    value = path or os.environ.get("DATABASE_URL") or ""
    return value if value.startswith(("postgres://","postgresql://")) else None
class _PG:
    def __init__(self, url):
        import psycopg
        from psycopg.rows import dict_row
        self.conn = psycopg.connect(url, row_factory=dict_row, connect_timeout=10)
    def execute(self, sql, params=()):
        return self.conn.execute(sql.replace("?", "%s"), params)
    def __enter__(self):
        self.conn.__enter__(); return self
    def __exit__(self, *args):
        return self.conn.__exit__(*args)
def connect(db_path=None):
    url = _pg_url(db_path)
    if url: return _PG(url)
    path = db_path or os.environ.get("KONSUMO_DB_PATH")
    if not path:
        from .config import DEFAULT_DB_PATH
        path = DEFAULT_DB_PATH
    c = sqlite3.connect(path, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("PRAGMA busy_timeout=30000")
    return c
def _init_db_uncached(db_path=None):
    if _pg_url(db_path):
        with connect(db_path) as c:
            # Serialize cold-start schema setup across concurrent Vercel functions.
            # Without this transaction-scoped lock, simultaneous CREATE TABLE IF NOT
            # EXISTS statements can race while PostgreSQL creates the table's row type.
            c.execute("SELECT pg_advisory_xact_lock(hashtext('konsumo_schema_init'))")
            for sql in PG_SCHEMA: c.execute(sql)
            c.execute("ALTER TABLE consumption ADD COLUMN IF NOT EXISTS user_id BIGINT REFERENCES users(id) ON DELETE CASCADE")
            first = c.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
            if first: c.execute("UPDATE consumption SET user_id=? WHERE user_id IS NULL", (first["id"],))
        return
    path = db_path or os.environ.get("KONSUMO_DB_PATH")
    if not path:
        from .config import DEFAULT_DB_PATH
        path = DEFAULT_DB_PATH
    target = os.path.abspath(path); os.makedirs(os.path.dirname(target), exist_ok=True)
    legacy = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "konsumo.sqlite3")
    if os.environ.get("KONSUMO_DB_PATH") and target == os.path.abspath(os.environ["KONSUMO_DB_PATH"]) and not os.path.exists(target) and os.path.isfile(legacy) and target != legacy:
        shutil.copy2(legacy, target)
    with connect(target) as c:
        c.executescript(SQLITE_SCHEMA)
        cols = {r["name"] for r in c.execute("PRAGMA table_info(consumption)")}
        if "user_id" not in cols:
            c.execute("ALTER TABLE consumption ADD COLUMN user_id INTEGER REFERENCES users(id)")
            first = c.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
            if first: c.execute("UPDATE consumption SET user_id=? WHERE user_id IS NULL", (first["id"],))
        c.execute("CREATE INDEX IF NOT EXISTS idx_consumption_user_resource_date ON consumption(user_id, resource, recorded_at)")


# Schema setup is needed once per database per warm serverless process, not on
# every HTTP request. Keep the lock process-local; PostgreSQL's advisory lock
# above still protects concurrent cold starts across separate instances.
_INIT_LOCK = threading.Lock()
_INITIALIZED_DATABASES = set()

def init_db(db_path=None):
    url = _pg_url(db_path)
    if url:
        key = "postgres:" + url
    else:
        path = db_path or os.environ.get("KONSUMO_DB_PATH")
        if not path:
            from .config import DEFAULT_DB_PATH
            path = DEFAULT_DB_PATH
        key = "sqlite:" + os.path.abspath(path)
    if key in _INITIALIZED_DATABASES:
        return
    with _INIT_LOCK:
        if key in _INITIALIZED_DATABASES:
            return
        _init_db_uncached(db_path)
        _INITIALIZED_DATABASES.add(key)
