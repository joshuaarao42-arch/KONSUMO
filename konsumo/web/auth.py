"""Username authentication with PBKDF2 password hashes and opaque sessions."""
import hashlib
import hmac
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from ..database import connect, init_db

ITERATIONS = 600_000
SESSION_DAYS = 14
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,24}$")


class AuthError(ValueError):
    pass


def _hash_password(password, salt=None, iterations=ITERATIONS):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return salt.hex(), digest.hex()


def _validate_password(password):
    if len(password) < 12:
        raise AuthError("Use a password with at least 12 characters.")
    if len(password) > 128:
        raise AuthError("Your password must be 128 characters or fewer.")
    classes = sum(bool(re.search(pattern, password)) for pattern in
                  (r"[a-z]", r"[A-Z]", r"\d", r"[^A-Za-z0-9]"))
    if classes < 3:
        raise AuthError("Use at least three of these: lowercase, uppercase, number, and symbol.")


def create_user(name, username, password, db_path=None):
    name = (name or "").strip()
    username = (username or "").strip().lower()
    if not name or len(name) > 80:
        raise AuthError("Enter your name (maximum 80 characters).")
    if not USERNAME_RE.fullmatch(username):
        raise AuthError("Username must be 3–24 characters: lowercase letters, numbers, and underscores.")
    _validate_password(password or "")
    init_db(db_path)
    salt, digest = _hash_password(password)
    # Keep the legacy email column populated for backward-compatible database schemas.
    legacy_email = username + "@users.konsumo.invalid"
    try:
        with connect(db_path) as c:
            uid = c.execute(
                "INSERT INTO users(name,email,username,password_salt,password_hash) VALUES (?,?,?,?,?) RETURNING id",
                (name, legacy_email, username, salt, digest),
            ).fetchone()["id"]
            return {"id": uid, "name": name, "username": username}
    except Exception as exc:
        if isinstance(exc, sqlite3.IntegrityError) or "unique" in str(exc).lower():
            raise AuthError("That username is already taken. Choose another one.") from exc
        raise


def authenticate(username, password, db_path=None):
    init_db(db_path)
    username = (username or "").strip().lower()
    with connect(db_path) as c:
        user = c.execute(
            "SELECT id,name,username,password_salt,password_hash,password_iterations FROM users WHERE lower(username)=?",
            (username,),
        ).fetchone()
    if not user:
        _hash_password(password or "", bytes(16))
        raise AuthError("Incorrect username or password.")
    _, candidate = _hash_password(password or "", bytes.fromhex(user["password_salt"]), int(user["password_iterations"] or 310000))
    if not hmac.compare_digest(candidate, user["password_hash"]):
        raise AuthError("Incorrect username or password.")
    if int(user["password_iterations"] or 310000) < ITERATIONS:
        _, upgraded = _hash_password(password, bytes.fromhex(user["password_salt"]), ITERATIONS)
        with connect(db_path) as c:
            c.execute("UPDATE users SET password_hash=?,password_iterations=? WHERE id=?", (upgraded, ITERATIONS, user["id"]))
    return {"id": user["id"], "name": user["name"], "username": user["username"]}


def _token_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(user_id, db_path=None):
    token = secrets.token_urlsafe(32)
    expires = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat()
    with connect(db_path) as c:
        c.execute("INSERT INTO sessions(token,user_id,expires_at) VALUES (?,?,?)",
                  (_token_hash(token), user_id, expires))
    return token


def get_session_user(token, db_path=None):
    if not token:
        return None
    now = datetime.now(timezone.utc).isoformat()
    with connect(db_path) as c:
        row = c.execute(
            """SELECT users.id,users.name,users.username FROM sessions
               JOIN users ON users.id=sessions.user_id
               WHERE sessions.token IN (?,?) AND sessions.expires_at>?""",
            (_token_hash(token), token, now),
        ).fetchone()
        c.execute("DELETE FROM sessions WHERE expires_at<=?", (now,))
    return dict(row) if row else None


def delete_session(token, db_path=None):
    if token:
        with connect(db_path) as c:
            c.execute("DELETE FROM sessions WHERE token IN (?,?)", (_token_hash(token), token))
