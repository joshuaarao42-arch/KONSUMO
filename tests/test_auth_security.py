import hashlib
import sqlite3

import pytest

from konsumo.database import connect, init_db
from konsumo.repository import add_record, get_record, list_records
from konsumo.web.auth import AuthError, authenticate, create_session, create_user, delete_session, get_session_user


PASSWORD = "StrongPassword!42"


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "konsumo-test.sqlite3")
    init_db(path)
    return path


def test_username_signup_login_and_password_hash(db_path):
    user = create_user("Test User", "test_user", PASSWORD, db_path)
    assert user["username"] == "test_user"
    assert authenticate("TEST_USER", PASSWORD, db_path)["id"] == user["id"]
    with connect(db_path) as conn:
        row = conn.execute("SELECT password_hash,password_salt FROM users WHERE id=?", (user["id"],)).fetchone()
    assert PASSWORD not in row["password_hash"]
    assert len(row["password_hash"]) == 64
    assert row["password_salt"]


def test_rejects_weak_password_and_invalid_username(db_path):
    with pytest.raises(AuthError):
        create_user("Test", "valid_user", "short", db_path)
    with pytest.raises(AuthError):
        create_user("Test", "Invalid Username", PASSWORD, db_path)


def test_duplicate_username_is_rejected(db_path):
    create_user("First", "same_name", PASSWORD, db_path)
    with pytest.raises(AuthError, match="already taken"):
        create_user("Second", "SAME_NAME", PASSWORD, db_path)


def test_wrong_password_is_rejected(db_path):
    create_user("Test", "test_user", PASSWORD, db_path)
    with pytest.raises(AuthError, match="Incorrect"):
        authenticate("test_user", "WrongPassword!42", db_path)


def test_session_token_is_hashed_and_revocable(db_path):
    user = create_user("Test", "test_user", PASSWORD, db_path)
    token = create_session(user["id"], db_path)
    assert get_session_user(token, db_path)["id"] == user["id"]
    with connect(db_path) as conn:
        stored = conn.execute("SELECT token FROM sessions").fetchone()["token"]
    assert stored != token
    delete_session(token, db_path)
    assert get_session_user(token, db_path) is None


def test_legacy_email_accounts_receive_unique_usernames(tmp_path):
    path = str(tmp_path / "legacy.sqlite3")
    conn = sqlite3.connect(path)
    conn.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE COLLATE NOCASE, password_salt TEXT NOT NULL,
        password_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.execute("INSERT INTO users(name,email,password_salt,password_hash) VALUES (?,?,?,?)",
                 ("Legacy", "legacy.user@example.com", "00", "00"))
    conn.commit()
    conn.close()
    init_db(path)
    with connect(path) as conn:
        username = conn.execute("SELECT username FROM users WHERE id=1").fetchone()["username"]
    assert username.startswith("legacyuser")
    assert username


def test_records_are_isolated_by_account(db_path):
    first = create_user("First", "first_user", PASSWORD, db_path)
    second = create_user("Second", "second_user", PASSWORD, db_path)
    record_id = add_record("electricity", "2026-11-16", 10, db_path=db_path, user_id=first["id"])
    assert get_record(record_id, db_path, first["id"]) is not None
    assert get_record(record_id, db_path, second["id"]) is None
    assert len(list_records(db_path=db_path, user_id=first["id"])) == 1
    assert list_records(db_path=db_path, user_id=second["id"]) == []


def test_vercel_signup_login_logout_and_security_headers(tmp_path, monkeypatch):
    from api import index as api

    monkeypatch.setattr(api, "DB", str(tmp_path / "api.sqlite3"))
    client = api.app.test_client()
    origin = {"Origin": "http://localhost"}

    health = client.get("/api/index?__path=/api/health")
    assert health.status_code == 200
    assert health.get_json()["database"] == "connected"

    mismatch = client.post("/signup", data={"name": "Bad", "username": "bad_user", "password": PASSWORD,
                                             "confirm_password": "DifferentPassword!42"}, headers=origin)
    assert mismatch.status_code == 400

    blocked = client.post("/signup", data={"name": "Bad", "username": "bad_user", "password": PASSWORD,
                                            "confirm_password": PASSWORD}, headers={"Origin": "https://evil.example"})
    assert blocked.status_code == 403

    created = client.post("/signup", data={"name": "Web User", "username": "web_user", "password": PASSWORD,
                                            "confirm_password": PASSWORD}, headers=origin)
    assert created.status_code == 303
    assert "HttpOnly" in created.headers.get("Set-Cookie", "")
    assert "SameSite=Lax" in created.headers.get("Set-Cookie", "")
    assert created.headers.get("X-Frame-Options") == "DENY"
    assert created.headers.get("X-Content-Type-Options") == "nosniff"

    dashboard = client.get("/")
    assert dashboard.status_code == 200
    assert "Dashboard" in dashboard.get_data(as_text=True)

    logged_out = client.post("/logout", headers=origin)
    assert logged_out.status_code == 303
    login = client.post("/login", data={"username": "web_user", "password": PASSWORD}, headers=origin)
    assert login.status_code == 303



def test_legacy_password_hash_is_accepted_then_upgraded(tmp_path):
    path = str(tmp_path / "legacy-password.sqlite3")
    password = "LegacyPassword!42"
    salt = bytes.fromhex("11" * 16)
    old_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000).hex()
    conn = sqlite3.connect(path)
    conn.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE COLLATE NOCASE, password_salt TEXT NOT NULL,
        password_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.execute("INSERT INTO users(name,email,password_salt,password_hash) VALUES (?,?,?,?)",
                 ("Legacy", "legacy.person@example.com", salt.hex(), old_hash))
    conn.commit()
    conn.close()
    init_db(path)
    with connect(path) as conn:
        username = conn.execute("SELECT username FROM users WHERE id=1").fetchone()["username"]
    assert authenticate(username, password, path)["id"] == 1
    with connect(path) as conn:
        row = conn.execute("SELECT password_iterations FROM users WHERE id=1").fetchone()
    assert row["password_iterations"] == 600000
