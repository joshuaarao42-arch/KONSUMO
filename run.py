#!/usr/bin/env python3
"""Konsumo launcher."""

from konsumo.config import DEFAULT_DB_PATH
from konsumo.database import init_db
from konsumo.web.app import run_server
import os

if __name__ == "__main__":
    init_db(DEFAULT_DB_PATH)
    port = int(os.environ.get("PORT", "5000"))
    run_server(DEFAULT_DB_PATH, "0.0.0.0", port)
