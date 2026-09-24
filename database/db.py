import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    database_url = None

    try:
        from flask import current_app, has_app_context
        if has_app_context():
            database_url = current_app.config.get("DATABASE_URL")
    except Exception:
        pass

    if not database_url:
        database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg2.connect(
        database_url,
        sslmode="require",
        connect_timeout=10,
        cursor_factory=RealDictCursor
    )