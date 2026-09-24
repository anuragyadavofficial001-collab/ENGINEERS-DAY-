# ============================================================
# ENGINEERS DAY - MAIN APPLICATION
# Supabase PostgreSQL + Vercel Ready
# ============================================================

import os
from datetime import timedelta

from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from database.db import get_db_connection


# ============================================================
# CREATE FLASK APP
# ============================================================

app = Flask(__name__)

app.config.from_object(Config)

# Enable ProxyFix to correctly handle reverse proxies on Vercel
# (X-Forwarded-For, X-Forwarded-Proto, X-Forwarded-Host)
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)


# ============================================================
# SESSION SECURITY
# ============================================================

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Secure cookie in production (Vercel uses HTTPS)
is_production = os.getenv("VERCEL") == "1" or os.getenv("FLASK_ENV") == "production"
app.config["SESSION_COOKIE_SECURE"] = bool(is_production)

app.permanent_session_lifetime = timedelta(
    hours=4
)


# ============================================================
# REGISTER ROUTES
# ============================================================

from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp
from routes.games import games_bp


app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(games_bp)


# ============================================================
# HOME / LANDING PAGE
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# DATABASE TEST
# ============================================================
#
# Temporary route for checking Supabase PostgreSQL connection.
# Remove this route after deployment/database testing is complete.
#

@app.route("/db-test")
def db_test():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) AS total_events FROM games"
        )

        result = cursor.fetchone()

        return f"""
        <h1>Database Connected Successfully ✅</h1>

        <p>
            Total Events:
            {result['total_events']}
        </p>
        """

    except Exception as e:

        return f"""
        <h1>Database Connection Failed ❌</h1>

        <p>
            {e}
        </p>
        """

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000
    )