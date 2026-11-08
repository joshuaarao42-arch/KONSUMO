"""Zero-dependency web server for the Konsumo dashboard (Python stdlib only).

Routing, form parsing, HTML pages and JSON API are all served by http.server,
so the dashboard runs with only pandas/numpy installed.
"""

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .. import __version__
from ..analytics import (daily_series, detect_anomalies, monthly_summary,
                         month_over_month, tiered_cost, usage_stats)
from ..config import CURRENCY
from ..database import init_db
from ..forecasting import forecast_all, forecast_daily
from ..recommendations import generate_recommendations
from ..repository import (LookupError, ValidationError, add_record, delete_record,
                          get_record, list_records, update_record)
from ..seed import seed as seed_db
from . import views
from .auth import AuthError, authenticate, create_session, create_user, delete_session, get_session_user
from http.cookies import SimpleCookie

RESOURCES = ("electricity", "water")


class Response:
    def __init__(self, body="", status=200,
                 content_type="text/html; charset=utf-8", redirect_to=None, headers=None):
        self.body, self.status = body, status
        self.content_type, self.redirect_to = content_type, redirect_to
        self.headers = headers or {}


def json_response(obj, status=200):
    return Response(json.dumps(obj), status, "application/json; charset=utf-8")


# ---------------------------------------------------------------- pages

def page_dashboard(p, q, form, db, user_id):
    cards = [{"resource": r, "stats": usage_stats(r, db_path=db, user_id=user_id),
              "mom": month_over_month(r, db_path=db, user_id=user_id)} for r in RESOURCES]
    try:
        forecasts = forecast_all(db_path=db, user_id=user_id)
    except ValueError:
        forecasts = {}
    anom = sum(len(detect_anomalies(r, db_path=db, user_id=user_id)) for r in RESOURCES)
    return Response(views.dashboard_page(cards, forecasts, anom, CURRENCY, __version__))


def page_records(p, q, form, db, user_id):
    resource = (q.get("resource") or [""])[0] or None
    query = (q.get("q") or [""])[0]
    page_no = max(1, int((q.get("page") or ["1"])[0]))
    limit = 25
    rows = list_records(resource=resource, limit=limit,
                        offset=(page_no - 1) * limit, db_path=db, user_id=user_id)
    if query:
        rows = [r for r in rows
                if query.lower() in (r["notes"] or "").lower()
                or query in str(r["recorded_at"])]
    return Response(views.records_page(rows, resource, query, page_no, limit,
                                       CURRENCY, __version__))


def page_record_new(p, q, form, db, user_id):
    return Response(views.record_form_page(None, CURRENCY, __version__))


def page_record_edit(p, q, form, db, user_id):
    record = get_record(int(p[0]), db_path=db, user_id=user_id)
    if not record:
        return Response(views.error_page(f"Record {p[0]} not found", __version__), 404)
    return Response(views.record_form_page(record, CURRENCY, __version__))


def _save_record(record_id, form, db, user_id):
    try:
        fields = dict(
            resource=form.get("resource"),
            recorded_at=form.get("recorded_at"),
            amount=float(form.get("amount") or 0),
            cost=float(form["cost"]) if form.get("cost") else None,
            notes=form.get("notes", ""),
        )
    except ValueError:
        return Response(views.error_page("Amount/cost must be numbers", __version__), 400)
    try:
        if record_id is None:
            add_record(db_path=db, user_id=user_id, **fields)
        else:
            update_record(record_id, db_path=db, user_id=user_id, **fields)
    except ValidationError as exc:
        return Response(views.error_page(str(exc), __version__), 400)
    return Response(status=302, redirect_to="/records")


def save_record_new(p, q, form, db, user_id):
    return _save_record(None, form, db, user_id)


def save_record_edit(p, q, form, db, user_id):
    return _save_record(int(p[0]), form, db, user_id)


def record_delete(p, q, form, db, user_id):
    try:
        delete_record(int(p[0]), db_path=db, user_id=user_id)
    except LookupError:
        return Response(views.error_page(f"Record {p[0]} not found", __version__), 404)
    return Response(status=302, redirect_to="/records")


def page_analytics(p, q, form, db, user_id):
    return Response(views.analytics_page(CURRENCY, __version__))


def page_forecast(p, q, form, db, user_id):
    try:
        fcs = forecast_all(db_path=db)
    except ValueError as exc:
        return Response(views.forecast_page({}, CURRENCY, __version__, str(exc)))
    return Response(views.forecast_page(fcs, CURRENCY, __version__))


def page_anomalies(p, q, form, db, user_id):
    data = {r: detect_anomalies(r, db_path=db) for r in RESOURCES}
    return Response(views.anomalies_page(data, CURRENCY, __version__))


def page_recommendations(p, q, form, db, user_id):
    tips = generate_recommendations(db_path=db, user_id=user_id)
    return Response(views.recommendations_page(tips, CURRENCY, __version__))


# ---------------------------------------------------------------- JSON API

def api_daily(p, q, form, db, user_id):
    s = daily_series(p[0], db_path=db, user_id=user_id)
    start = (q.get("start") or [None])[0]
    if start:
        s = s[s.index >= start]
    return json_response([{"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 3)}
                          for d, v in s.items()])


def api_monthly(p, q, form, db, user_id):
    m = monthly_summary(p[0], months=14, db_path=db, user_id=user_id)
    return json_response([{"month": i.strftime("%Y-%m"),
                           "usage": round(float(r["usage"]), 2),
                           "cost": round(float(r["cost"]), 2)}
                          for i, r in m.iterrows()])


def api_forecast(p, q, form, db, user_id):
    try:
        fc, metrics = forecast_daily(p[0], db_path=db, user_id=user_id)
    except ValueError as exc:
        return json_response({"error": str(exc)}, 400)
    hist = daily_series(p[0], db_path=db).tail(60)
    return json_response({
        "metrics": metrics,
        "points": [{"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 3)}
                   for d, v in fc.items()],
        "history": [{"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 3)}
                    for d, v in hist.items()],
    })


def api_stats(p, q, form, db, user_id):
    return json_response(usage_stats(p[0], db_path=db, user_id=user_id))


def api_quote(p, q, form, db, user_id):
    body = form.get("_json") or {}
    try:
        amount = float(body.get("amount"))
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return json_response({"error": "amount must be a positive number"}, 400)
    resource = body.get("resource", "electricity")
    if resource not in RESOURCES:
        return json_response({"error": "unknown resource"}, 400)
    return json_response({"resource": resource, "amount": amount,
                          "cost": tiered_cost(amount, resource), "currency": CURRENCY})


def api_seed(p, q, form, db, user_id):
    created = seed_db(db_path=db, days=int(form.get("days", 425)), verbose=False, user_id=user_id)
    return json_response({"created": created})


def static_css(p, q, form, db, user_id):
    return Response(views.STYLE, 200, "text/css; charset=utf-8")


ROUTES = [
    ("GET",  r"^/$",                     page_dashboard),
    ("GET",  r"^/records$",              page_records),
    ("GET",  r"^/records/new$",          page_record_new),
    ("POST", r"^/records/new$",          save_record_new),
    ("GET",  r"^/records/(\d+)/edit$",   page_record_edit),
    ("POST", r"^/records/(\d+)/edit$",   save_record_edit),
    ("POST", r"^/records/(\d+)/delete$", record_delete),
    ("GET",  r"^/analytics$",            page_analytics),
    ("GET",  r"^/forecast$",             page_forecast),
    ("GET",  r"^/anomalies$",            page_anomalies),
    ("GET",  r"^/recommendations$",      page_recommendations),
    ("GET",  r"^/api/daily/(\w+)$",      api_daily),
    ("GET",  r"^/api/monthly/(\w+)$",    api_monthly),
    ("GET",  r"^/api/forecast/(\w+)$",   api_forecast),
    ("GET",  r"^/api/stats/(\w+)$",      api_stats),
    ("POST", r"^/api/quote$",            api_quote),
    ("POST", r"^/api/seed$",             api_seed),
    ("GET",  r"^/static/style\.css$",    static_css),
]


def route(method, path, query, form, db, user_id):
    for m, pattern, fn in ROUTES:
        if m != method:
            continue
        match = re.match(pattern, path)
        if match:
            return fn(match.groups(), query, form, db, user_id)
    return Response(views.error_page("Page not found", __version__), 404)


def make_handler(db):
    class Handler(BaseHTTPRequestHandler):
        server_version = f"Konsumo/{__version__}"

        def log_message(self, fmt, *args):  # quiet console; errors still raised
            pass

        def _dispatch(self, method):
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/") or "/"
            query = parse_qs(parsed.query)
            form = {}
            if method == "POST":
                length = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(length) if length else b""
                if "application/json" in (self.headers.get("Content-Type") or ""):
                    try:
                        form["_json"] = json.loads(raw or b"{}")
                    except json.JSONDecodeError:
                        form["_json"] = {}
                else:
                    form = {k: v[0] for k, v in parse_qs(raw.decode()).items()}
            try:
                cookies = SimpleCookie()
                try:
                    cookies.load(self.headers.get("Cookie", ""))
                except Exception:
                    pass
                morsel = cookies.get("konsumo_session")
                token = morsel.value if morsel else ""
                secure = "; Secure" if self.headers.get("X-Forwarded-Proto", "").lower() == "https" else ""
    
                if path in ("/login", "/signup"):
                    if method == "GET":
                        resp = Response(views.auth_page("login" if path == "/login" else "signup"))
                    elif method == "POST":
                        try:
                            if path == "/signup":
                                user = create_user(form.get("name", ""), form.get("email", ""), form.get("password", ""), db)
                            else:
                                user = authenticate(form.get("email", ""), form.get("password", ""), db)
                            session_token = create_session(user["id"], db)
                            resp = Response(status=303, redirect_to="/",
                                headers={"Set-Cookie": f"konsumo_session={session_token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=1209600{secure}"})
                        except AuthError as exc:
                            resp = Response(views.auth_page("login" if path == "/login" else "signup", str(exc), form), 400)
                    else:
                        resp = Response(views.error_page("Method not allowed", __version__), 405)
                elif path == "/logout" and method == "POST":
                    delete_session(token, db)
                    resp = Response(status=303, redirect_to="/login",
                        headers={"Set-Cookie": "konsumo_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0" + secure})
                else:
                    user = get_session_user(token, db)
                    if not user:
                        resp = Response(status=303, redirect_to="/login")
                    else:
                        resp = route(method, path, query, form, db, user["id"])
    
            except Exception as exc:  # pragma: no cover - safety net
                resp = Response(views.error_page(f"Internal error: {exc}", __version__), 500)
            payload = (resp.body.encode("utf-8")
                       if isinstance(resp.body, str) else resp.body)
            self.send_response(resp.status)
            self.send_header("Content-Type", resp.content_type)
            self.send_header("Content-Length", str(len(payload)))
            if resp.redirect_to:
                self.send_header("Location", resp.redirect_to)
            for header, value in resp.headers.items():
                self.send_header(header, value)
            self.end_headers()
            if payload:
                self.wfile.write(payload)

        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

    return Handler


def create_server(db_path, host="127.0.0.1", port=5000):
    init_db(db_path)
    server = ThreadingHTTPServer((host, port), make_handler(db_path))
    server.daemon_threads = True
    return server


def run_server(db_path, host="127.0.0.1", port=5000):
    server = create_server(db_path, host, port)
    print(f"Konsumo dashboard → http://{host}:{server.server_address[1]}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()
