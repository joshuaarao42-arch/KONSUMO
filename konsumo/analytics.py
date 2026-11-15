import math

import numpy as np
import pandas as pd
from .config import TARIFFS
from .database import connect


def _frame(resource, db_path, user_id):
    if user_id is None:
        return pd.DataFrame(columns=["recorded_at", "amount", "cost"])
    with connect(db_path) as c:
        rows = c.execute(
            "SELECT recorded_at,amount,cost FROM consumption "
            "WHERE resource=? AND user_id=? ORDER BY recorded_at",
            (resource, user_id),
        ).fetchall()
    if not rows:
        return pd.DataFrame(columns=["recorded_at", "amount", "cost"])
    frame = pd.DataFrame([dict(row) for row in rows])
    frame["recorded_at"] = pd.to_datetime(frame["recorded_at"])
    return frame


def tiered_cost(amount, resource="electricity"):
    total = 0.0
    prior = 0.0
    for cap, rate in TARIFFS[resource]:
        take = min(max(float(amount) - prior, 0), cap - prior)
        total += take * rate
        prior = cap
        if amount <= cap:
            break
    return round(total, 2)


def daily_series(resource, db_path, user_id=None):
    frame = _frame(resource, db_path, user_id)
    if frame.empty:
        return pd.Series(dtype=float)
    return frame.set_index("recorded_at")["amount"].resample("D").sum()


def monthly_summary(resource, months=14, db_path=None, user_id=None):
    frame = _frame(resource, db_path, user_id)
    if frame.empty:
        return pd.DataFrame(columns=["usage", "cost"])
    return (
        frame.set_index("recorded_at")
        .resample("MS")
        .agg(usage=("amount", "sum"), cost=("cost", "sum"))
        .tail(months)
    )


def _finite_number(value, default=0.0):
    """Convert analytics output to a finite number safe for JSON and UI rendering."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return round(number, 2) if math.isfinite(number) else default


def usage_stats(resource, db_path, user_id=None):
    series = daily_series(resource, db_path, user_id)
    if series.empty:
        return {
            "resource": resource,
            "count": 0,
            "total": 0.0,
            "average": 0.0,
            "maximum": 0.0,
        }
    return {
        "resource": resource,
        "count": int(series.count()),
        "total": _finite_number(series.sum()),
        "average": _finite_number(series.mean()),
        "maximum": _finite_number(series.max()),
    }


def month_over_month(resource, db_path, user_id=None):
    monthly = monthly_summary(resource, 2, db_path, user_id)
    if len(monthly) < 2:
        return 0
    previous = _finite_number(monthly.iloc[-2].usage)
    current = _finite_number(monthly.iloc[-1].usage)
    if previous <= 0:
        return 0
    return _finite_number(current / previous - 1, 0.0)


def detect_anomalies(resource, db_path, user_id=None):
    series = daily_series(resource, db_path, user_id)
    if len(series) < 3:
        return []
    mean = float(series.mean())
    std = float(series.std())
    if not math.isfinite(mean) or not math.isfinite(std) or std <= 0:
        return []
    results = []
    for date, value in series.items():
        z_score = (float(value) - mean) / std
        if math.isfinite(z_score) and abs(z_score) >= 2.5:
            results.append({
                "date": date.strftime("%Y-%m-%d"),
                "amount": _finite_number(value, 0.0),
                "z_score": round(z_score, 2),
                "cost": tiered_cost(value, resource),
            })
    return results
