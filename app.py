# ============================================================
# ENGINEERS DAY - MAIN APPLICATION
# ============================================================

from datetime import timedelta

from flask import Flask

from flask import Flask, render_template

import pymysql

from config import Config

from database.db import get_db_connection



# ============================================================
# CREATE FLASK APP
# ============================================================

app = Flask(__name__)

app.config.from_object(Config)


# ============================================================
# SESSION SECURITY
# ============================================================

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["SESSION_COOKIE_SECURE"] = False
# False for local development.
# Change to True when deployed with HTTPS.

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
app.register_blueprint(
    auth_bp
)

app.register_blueprint(
    student_bp
)

app.register_blueprint(admin_bp)

app.register_blueprint(games_bp)
# ============================================================
# DEVELOPMENT HOME
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# DATABASE TEST
# ============================================================

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
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )