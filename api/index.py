"""Vercel-compatible Flask entry point for Konsumo."""
import os, hashlib, time
from urllib.parse import urlsplit
from flask import Flask, request, make_response
from konsumo.config import DEFAULT_DB_PATH
from konsumo.database import init_db
from konsumo.web import views
from konsumo.web.app import Response as AppResponse, route
from konsumo.web.auth import AuthError, authenticate, create_session, create_user, delete_session, get_session_user

app=Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
DB=os.environ.get("DATABASE_URL") or DEFAULT_DB_PATH

def _client_ip():
    forwarded = request.headers.get("x-vercel-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()[:100]
    return request.remote_addr or "unknown"


def _rate_limit(scope, limit, window_seconds, subject=""):
    identity = hashlib.sha256((_client_ip() + "|" + subject).encode()).hexdigest()
    now = int(time.time())
    window_start = now - (now % window_seconds)
    with connect_db(DB) as conn:
        row = conn.execute(
            """INSERT INTO konsumo_rate_limits(scope,identity_hash,window_start,hit_count)
               VALUES (?,?,?,1)
               ON CONFLICT(scope,identity_hash,window_start)
               DO UPDATE SET hit_count=hit_count+1
               RETURNING hit_count""",
            (scope, identity, window_start),
        ).fetchone()
        if now % 3600 < 5:
            conn.execute("DELETE FROM konsumo_rate_limits WHERE window_start < ?", (now - 172800,))
    return row["hit_count"] <= limit


from konsumo.database import connect as connect_db


def _csrf_rejected(path):
    origin = request.headers.get("Origin")
    if not origin:
        return True
    if urlsplit(origin).netloc.lower() != request.host.lower() or urlsplit(origin).scheme not in ("http", "https"):
        return True
    if request.headers.get("Sec-Fetch-Site", "").lower() == "cross-site":
        return True
    if path.startswith("/api/") and request.method in ("POST", "PUT", "PATCH", "DELETE"):
        return request.headers.get("X-KONSUMO-Request") != "1"
    return False


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https://generativelanguage.googleapis.com"
    if request.is_secure or request.headers.get("x-forwarded-proto") == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/",defaults={"subpath":""},methods=["GET","POST"])
@app.route("/<path:subpath>",methods=["GET","POST"])
def dispatch(subpath):
    # Vercel rewrites requests to /api/index; recover the original URL path.
    path=request.args.get("__path") or ("/"+subpath if subpath else "/")
    if not path.startswith("/"):
        path="/"+path
    method=request.method
    if method in ("POST", "PUT", "PATCH", "DELETE") and _csrf_rejected(path):
        return make_response("Request rejected.", 403)
    query={k:v for k,v in request.args.to_dict(flat=False).items() if k != "__path"}
    form=request.form.to_dict()
    if request.is_json: form["_json"]=request.get_json(silent=True) or {}
    # Static browser icon requests do not need authentication or a database connection.
    if path in ("/favicon.ico", "/favicon.png"):
        return make_response("", 204)

    try:
        # Login and signup GETs only render HTML; defer the database connection
        # until a form is submitted or a protected page needs session lookup.
        if not (method == "GET" and path in ("/login", "/signup")):
            init_db(DB)
        if method == "POST" and path == "/signup" and not _rate_limit("signup", 5, 3600):
            return make_response("Too many signup attempts. Please try again later.", 429)
        if method == "POST" and path == "/login" and (not _rate_limit("login_ip", 30, 900) or not _rate_limit("login_user", 10, 900, str(form.get("username", "")).lower())):
            return make_response("Too many login attempts. Please try again later.", 429)
        if method == "POST" and path == "/api/seed" and not _rate_limit("seed", 5, 3600):
            return make_response('{"error":"Sample-data generation limit reached. Try again later."}', 429, {"Content-Type":"application/json"})
        if method == "POST" and path == "/api/chat" and not _rate_limit("ai", 30, 3600):
            return make_response('{"error":"AI request limit reached. Try again later."}', 429, {"Content-Type":"application/json"})
        if method == "POST" and path.startswith("/records") and not _rate_limit("records", 120, 3600):
            return make_response("Too many changes. Please try again later.", 429)
        token=request.cookies.get("konsumo_session","")
        secure=bool(os.environ.get("VERCEL")) or request.is_secure
        if path in ("/login","/signup"):
            if method=="GET": result=AppResponse(views.auth_page("login" if path=="/login" else "signup"))
            else:
                try:
                    if path=="/signup":
                        if form.get("password","") != form.get("confirm_password",""): raise AuthError("Your passwords do not match.")
                        user=create_user(form.get("name",""),form.get("username",""),form.get("password",""),DB)
                    else: user=authenticate(form.get("username",""),form.get("password",""),DB)
                    session=create_session(user["id"],DB)
                    result=AppResponse(status=303,redirect_to="/",headers={"Set-Cookie":f"konsumo_session={session}; Path=/; HttpOnly; SameSite=Lax; Max-Age=1209600"+("; Secure" if secure else "")})
                except AuthError as exc: result=AppResponse(views.auth_page("login" if path=="/login" else "signup",str(exc),form),400)
        elif path=="/logout" and method=="POST":
            delete_session(token,DB)
            result=AppResponse(status=303,redirect_to="/login",headers={"Set-Cookie":"konsumo_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"+("; Secure" if secure else "")})
        else:
            user=get_session_user(token,DB)
            result=route(method,path,query,form,DB,user["id"]) if user else AppResponse(status=303,redirect_to="/login")
        response=make_response(result.body or "",result.status)
        response.headers["Content-Type"]=result.content_type
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if result.redirect_to: response.headers["Location"]=result.redirect_to
        for key,value in result.headers.items(): response.headers[key]=value
        return response
    except Exception:
        app.logger.exception("Konsumo request failed")
        return make_response(
            "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Konsumo error</title></head><body style='font-family:system-ui;max-width:560px;margin:12vh auto;padding:24px;color:#172033'><h1>Something went wrong</h1><p>Konsumo could not complete this request. Please try again in a moment.</p><p><a href='/login'>Return to login</a></p></body></html>",
            500,
        )

@app.get("/api/health")
def health():
    try:
        init_db(DB)
        return {"status":"ok","database":"connected"}
    except Exception:
        app.logger.exception("Database health check failed")
        return {"status":"error","database":"unavailable"},503
