"""Password-based account authentication and server-side sessions."""
import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from ..database import connect, init_db

ITERATIONS = 310_000
SESSION_DAYS = 14

class AuthError(ValueError):
    pass

def _hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return salt.hex(), digest.hex()

def create_user(name, email, password, db_path):
    name, email = name.strip(), email.strip().lower()
    if not name or len(name) > 80:
        raise AuthError("Please enter your name (maximum 80 characters).")
    if (len(email) > 254 or email.count("@") != 1 or
            email.startswith("@") or email.endswith("@") or
            "." not in email.rsplit("@", 1)[-1]):
        raise AuthError("Please enter a valid email address.")
    if len(password) < 8:
        raise AuthError("Your password must contain at least 8 characters.")
    if len(password) > 128:
        raise AuthError("Your password is too long.")
    init_db(db_path)
    salt, password_hash = _hash_password(password)
    try:
        with connect(db_path) as conn:
            cur = conn.execute(
                "INSERT INTO users(name,email,password_salt,password_hash) VALUES (?,?,?,?)",
                (name, email, salt, password_hash))
            return {"id": cur.lastrowid, "name": name, "email": email}
    except sqlite3.IntegrityError:
        raise AuthError("An account with that email already exists. Please log in.")

def authenticate(email, password, db_path):
    init_db(db_path)
    with connect(db_path) as conn:
        user = conn.execute(
            "SELECT id,name,email,password_salt,password_hash FROM users WHERE email=?",
            (email.strip().lower(),)).fetchone()
    if not user:
        _hash_password(password, bytes(16))
        raise AuthError("Incorrect email or password.")
    _, candidate = _hash_password(password, bytes.fromhex(user["password_salt"]))
    if not hmac.compare_digest(candidate, user["password_hash"]):
        raise AuthError("Incorrect email or password.")
    return {"id": user["id"], "name": user["name"], "email": user["email"]}

def create_session(user_id, db_path):
    token = secrets.token_urlsafe(32)
    expires = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat()
    with connect(db_path) as conn:
        conn.execute("INSERT INTO sessions(token,user_id,expires_at) VALUES (?,?,?)",
                     (token, user_id, expires))
    return token

def get_session_user(token, db_path):
    if not token:
        return None
    now = datetime.now(timezone.utc).isoformat()
    with connect(db_path) as conn:
        row = conn.execute("""SELECT users.id, users.name, users.email
                              FROM sessions JOIN users ON users.id=sessions.user_id
                              WHERE sessions.token=? AND sessions.expires_at>?""",
                           (token, now)).fetchone()
        conn.execute("DELETE FROM sessions WHERE expires_at<=?", (now,))
    return dict(row) if row else None

def delete_session(token, db_path):
    if token:
        with connect(db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE token=?", (token,))
