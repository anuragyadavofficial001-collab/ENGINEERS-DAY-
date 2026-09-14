# ============================================================
# ENGINEERS DAY - STUDENT PANEL
# ============================================================

from functools import wraps

from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for,
)

from database.db import get_db_connection


student_bp = Blueprint("student", __name__)


# ============================================================
# STUDENT AUTHENTICATION GUARD
# ============================================================

def student_login_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        # ----------------------------------------------------
        # Check authentication session
        # ----------------------------------------------------

        if not session.get("authenticated"):
            return redirect(url_for("auth.login"))

        # ----------------------------------------------------
        # Internal database student ID must exist
        # ----------------------------------------------------

        if not session.get("student_id"):
            session.clear()
            return redirect(url_for("auth.login"))

        return view_function(*args, **kwargs)

    return wrapped_view


# ============================================================
# STUDENT HOME / DASHBOARD
# ============================================================

@student_bp.route("/home", methods=["GET"])
@student_login_required
def home():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # Load authenticated student
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                student_id,
                name,
                email,
                phone,
                branch,
                section,
                year
            FROM students
            WHERE id = %s
              AND is_active = TRUE
            LIMIT 1
            """,
            (session["student_id"],)
        )

        student = cursor.fetchone()

        # ----------------------------------------------------
        # Session belongs to invalid / deleted / disabled user
        # ----------------------------------------------------

        if not student:

            session.clear()

            return redirect(url_for("auth.login"))

        # ----------------------------------------------------
        # Dashboard
        # ----------------------------------------------------

        return render_template(
            "home.html",
            student=student
        )

    except Exception:

        # Do NOT expose database errors to students.
        if connection:
            connection.rollback()

        return (
            "Unable to load your student dashboard. "
            "Please try again later."
        ), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()