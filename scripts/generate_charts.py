"""Render README screenshots with matplotlib (docs/screenshots/*.png)."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from konsumo.analytics import daily_series, monthly_summary, detect_anomalies
from konsumo.config import DEFAULT_DB_PATH
from konsumo.forecasting import forecast_daily

parser = argparse.ArgumentParser(description="Generate charts for one Konsumo account")
parser.add_argument("--user-id", type=int, required=True, help="Account ID whose data should appear in the charts")
USER_ID = parser.parse_args().user_id

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots")
os.makedirs(OUT, exist_ok=True)

for res, color in (("electricity", "#f59e0b"), ("water", "#0ea5e9")):
    s = daily_series(res, db_path=DEFAULT_DB_PATH, user_id=USER_ID).tail(90)
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.plot(s.index, s.values, color=color)
    ax.set_title(f"Daily {res} usage — last 90 days"); fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"daily_{res}.png"), dpi=130); plt.close(fig)

    fc, _ = forecast_daily(res, db_path=DEFAULT_DB_PATH)
    hist = daily_series(res, db_path=DEFAULT_DB_PATH).tail(60)
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.plot(hist.index, hist.values, color="#94a3b8", label="history")
    ax.plot(fc.index, fc.values, color=color, ls="--", label="forecast")
    ax.legend(); ax.set_title(f"{res.capitalize()} 30-day forecast"); fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"forecast_{res}.png"), dpi=130); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))
for ax, res in zip(axes, ("electricity", "water")):
    m = monthly_summary(res, months=14, db_path=DEFAULT_DB_PATH)
    ax.bar(m.index.strftime("%Y-%m"), m["usage"], color="#6366f1")
    ax.set_title(f"Monthly {res}"); ax.tick_params(axis="x", rotation=60)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "monthly_summary.png"), dpi=130)
plt.close(fig)
print("Screenshots written to", OUT)
