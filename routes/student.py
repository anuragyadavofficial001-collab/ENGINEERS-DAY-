# ============================================================
# ENGINEERS DAY 2026
# STUDENT ROUTES
# ============================================================

from functools import wraps

from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for
)

from database.db import get_db_connection


# ============================================================
# BLUEPRINT
# ============================================================

student_bp = Blueprint("student", __name__)


# ============================================================
# STUDENT LOGIN REQUIRED
# ============================================================

def student_login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        # Student must be authenticated
        if not session.get("authenticated"):
            return redirect(url_for("auth.login"))

        # Student ID must exist in session
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
        # ----------------------------------------------------
        # DATABASE CONNECTION
        # ----------------------------------------------------

        connection = get_db_connection()
        cursor = connection.cursor()


        # ----------------------------------------------------
        # LOAD LOGGED-IN STUDENT
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
        # STUDENT NOT FOUND
        # ----------------------------------------------------

        if not student:
            session.clear()
            return redirect(url_for("auth.login"))


        # ----------------------------------------------------
        # LOAD ALL 27 GAMES
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                game_name,
                description,
                prize_pool,
                requirements,
                rules,
                registration_mode,
                team_min_size,
                team_max_size,
                event_date,
                start_time,
                end_time,
                block,
                floor,
                room,
                status,
                registration_open,
                winner_certificate,
                runner_up_certificate
            FROM games
            ORDER BY id ASC
            """
        )

        games = cursor.fetchall()


        # ----------------------------------------------------
        # LOAD STUDENT REGISTRATIONS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                r.id AS registration_id,
                r.game_id,
                r.status AS registration_status,
                r.registered_at,
                g.game_name
            FROM registrations r
            INNER JOIN games g
                ON g.id = r.game_id
            WHERE r.student_id = %s
            ORDER BY r.registered_at DESC
            """,
            (student["id"],)
        )

        my_events = cursor.fetchall()


        # ----------------------------------------------------
        # TOTAL GAMES
        # ----------------------------------------------------

        total_games = len(games)


        # ----------------------------------------------------
        # JOINED GAMES
        # ----------------------------------------------------

        joined_games = sum(
            1
            for event in my_events
            if event["registration_status"] in (
                "REGISTERED",
                "APPROVED"
            )
        )


        # ----------------------------------------------------
        # UPCOMING GAMES
        # ----------------------------------------------------

        upcoming_games = sum(
            1
            for game in games
            if game["status"] == "UPCOMING"
            and game["registration_open"]
        )


        # ----------------------------------------------------
        # PUBLISHED RESULTS COUNT
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(*) AS result_count
            FROM results
            WHERE is_published = TRUE
            """
        )

        result_row = cursor.fetchone()

        results_available = (
            result_row["result_count"]
            if result_row
            else 0
        )


        # ----------------------------------------------------
        # LOAD PUBLISHED NOTIFICATIONS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                game_id,
                title,
                message,
                notification_type,
                published_at,
                expires_at
            FROM notifications
            WHERE is_published = TRUE
              AND (
                    expires_at IS NULL
                    OR expires_at > CURRENT_TIMESTAMP
                  )
            ORDER BY published_at DESC
            LIMIT 10
            """
        )

        notifications = cursor.fetchall()


        # ----------------------------------------------------
        # RENDER STUDENT DASHBOARD
        # ----------------------------------------------------

        return render_template(
            "home.html",
            student=student,
            games=games,
            my_events=my_events,
            notifications=notifications,
            total_games=total_games,
            joined_games=joined_games,
            upcoming_games=upcoming_games,
            results_available=results_available
        )


    # ========================================================
    # DATABASE / APPLICATION ERROR
    # ========================================================

    except Exception:

        if connection:
            connection.rollback()

        return (
            "Unable to load your student dashboard. "
            "Please try again later."
        ), 500


    # ========================================================
    # CLOSE DATABASE RESOURCES
    # ========================================================

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# STUDENT RESULTS
# ============================================================

@student_bp.route("/results", methods=["GET"])
@student_login_required
def results():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                r.id,
                r.game_id,
                g.game_name,
                r.winner_name,
                r.winner_roll_number,
                r.winner_department,
                r.runner_up_name,
                r.runner_up_roll_number,
                r.runner_up_department,
                r.remarks,
                r.published_at
            FROM results r
            INNER JOIN games g ON g.id = r.game_id
            WHERE r.is_published = TRUE
            ORDER BY r.published_at DESC, g.game_name ASC
            """
        )
        published_results = cursor.fetchall()

        return render_template(
            "results.html",
            results=published_results
        )

    except Exception:
        if connection:
            connection.rollback()
        return render_template("results.html", results=[])

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()