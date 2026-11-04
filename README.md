# Konsumo

Konsumo is a household utility-consumption tracker for electricity and water. It stores
meter readings in SQLite, bills them with tiered tariffs, flags unusual usage, forecasts
the next 30 days, and suggests ways to save, all from a small dashboard, a JSON API or a CLI.

## Features

- **CRUD** for consumption records (web form, API and CLI)
- **SQLite storage** (no server to run)
- **Tiered-tariff billing**: cost is computed automatically unless you override it
- **Anomaly detection**: rolling z-score with the cost impact of each anomaly
- **Forecasting**: ensemble forecast with the blend weight chosen automatically by holdout MAE
- **Recommendations engine** based on your own usage patterns
- **Interactive dashboard** built with Chart.js
- **JSON API** and a **command-line interface**

## Tech stack

Python 3.10+, stdlib `http.server`, SQLite, pandas, numpy, Chart.js.

## Installation

```bash
pip install -r requirements.txt
```

## Quickstart

```bash
python run.py
```

Then open <http://127.0.0.1:5000>. The first run seeds a demo database automatically.

## Accounts

Konsumo includes account registration and login pages. On a fresh database, create the initial account, then sign in with its email and password. For safety, public registration is limited to the first account; later visitors must log in rather than create additional accounts. Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes, and browser sessions use an HTTP-only cookie.

The initial account controls access to the household consumption dataset. Use a persistent database/storage volume in production so account and session records survive redeploys.

## CLI

```bash
python -m konsumo.cli stats
python -m konsumo.cli anomalies
python -m konsumo.cli forecast
python -m konsumo.cli recommend
python -m konsumo.cli add ...
python -m konsumo.cli list
python -m konsumo.cli update ...
python -m konsumo.cli delete ...
```

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/daily/<resource>` | GET | Daily usage series (optional `?start=YYYY-MM-DD`) |
| `/api/monthly/<resource>` | GET | Monthly usage and cost summary |
| `/api/forecast/<resource>` | GET | 30-day forecast, history and holdout metrics |
| `/api/stats/<resource>` | GET | Summary statistics |
| `/api/quote` | POST | Tariff cost for `{"resource": "...", "amount": n}` |

`<resource>` is `electricity` or `water`.

## Methodology

- **Anomalies:** rolling z-score, window = 30 days, threshold = 2.5. Falls back to global
  statistics when there is not enough history.
- **Forecast:** an ensemble of seasonal-naive and moving-average predictions plus a clipped
  linear trend. The blend weight is chosen on a 30-day holdout.

## Configuration

Edit `konsumo/config.py` for tariff tiers, thresholds and currency.

## Project structure

```
konsumo/
├── run.py
├── requirements.txt
├── konsumo/
│   ├── config.py  database.py  repository.py  seed.py  cli.py
│   ├── analytics.py  forecasting.py  recommendations.py
│   └── web/  app.py  views.py
├── scripts/generate_charts.py
├── tests/test_konsumo.py
└── docs/screenshots/
```

## Testing

```bash
python -m unittest discover tests -v
```

## Screenshots

Generate with `python scripts/generate_charts.py`.

![Daily electricity](docs/screenshots/daily_electricity.png)
![Daily water](docs/screenshots/daily_water.png)
![Monthly summary](docs/screenshots/monthly_summary.png)
![Electricity forecast](docs/screenshots/forecast_electricity.png)

## Roadmap

- CSV import/export
- Multiple households or meters
- Budget alerts
- More resources (gas)

## License

MIT, see [LICENSE](LICENSE).
