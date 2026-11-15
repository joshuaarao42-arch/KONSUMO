"""Vercel-compatible Flask entry point for Konsumo."""
import os
from flask import Flask, request, make_response
from konsumo.config import DEFAULT_DB_PATH
from konsumo.database import init_db
from konsumo.web import views
from konsumo.web.app import Response as AppResponse, route
from konsumo.web.auth import AuthError, authenticate, create_session, create_user, delete_session, get_session_user

app=Flask(__name__)
DB=os.environ.get("DATABASE_URL") or DEFAULT_DB_PATH

@app.route("/",defaults={"subpath":""},methods=["GET","POST"])
@app.route("/<path:subpath>",methods=["GET","POST"])
def dispatch(subpath):
    # Vercel rewrites requests to /api/index; recover the original URL path.
    path=request.args.get("__path") or ("/"+subpath if subpath else "/")
    if not path.startswith("/"):
        path="/"+path
    method=request.method
    query={k:v for k,v in request.args.to_dict(flat=False).items() if k != "__path"}
    form=request.form.to_dict()
    if request.is_json: form["_json"]=request.get_json(silent=True) or {}
    try:
        init_db(DB)
        token=request.cookies.get("konsumo_session","")
        secure=bool(os.environ.get("VERCEL")) or request.is_secure
        if path in ("/login","/signup"):
            if method=="GET": result=AppResponse(views.auth_page("login" if path=="/login" else "signup"))
            else:
                try:
                    if path=="/signup": user=create_user(form.get("name",""),form.get("email",""),form.get("password",""),DB)
                    else: user=authenticate(form.get("email",""),form.get("password",""),DB)
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
