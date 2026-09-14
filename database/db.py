import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app


def get_db_connection():
    database_url = current_app.config.get("DATABASE_URL") or os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg2.connect(
        database_url,
        sslmode="require",
        cursor_factory=RealDictCursor
    )