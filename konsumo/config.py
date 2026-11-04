from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = str(BASE_DIR / "konsumo.sqlite3")
CURRENCY = "PHP"
TARIFFS = {
    "electricity": ((100, 0.18), (300, 0.24), (float("inf"), 0.32)),
    "water": ((10, 1.20), (30, 1.75), (float("inf"), 2.40)),
}
