# ============================================================
# ENGINEERS DAY 2026
# STUDENT EVENT / GAMES ROUTES
# ============================================================

from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from database.db import get_db_connection


games_bp = Blueprint("games", __name__, url_prefix="/games")


# ============================================================
# STUDENT LOGIN PROTECTION
# ============================================================

def student_login_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if not session.get("authenticated"):
            return redirect(url_for("auth.login"))

        if not session.get("student_id"):
            session.clear()
            return redirect(url_for("auth.login"))

        return view_function(*args, **kwargs)

    return wrapped_view


# ============================================================
# HELPER
# ============================================================

def get_current_student():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                student_id,
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

        return cursor.fetchone()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# ALL EVENTS
# ============================================================

@games_bp.route("/")
@student_login_required
def games():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                description,
                registration_mode,
                team_min_size,
                team_max_size,
                event_date,
                start_time,
                end_time,
                venue,
                status,
                registration_open,
                prizes,
                rules,
                requirements
            FROM games
            WHERE status = 'UPCOMING'
               OR status = 'ONGOING'
               OR registration_open = TRUE
            ORDER BY
                event_date IS NULL,
                event_date ASC,
                start_time IS NULL,
                start_time ASC,
                id ASC
            """
        )

        games_list = cursor.fetchall()

        return render_template(
            "games.html",
            games=games_list
        )

    except Exception:

        if connection:
            connection.rollback()

        return render_template(
            "games.html",
            games=[],
            load_error=True
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# GAME DETAILS
# ============================================================

@games_bp.route("/<int:game_id>")
@student_login_required
def game_details(game_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # GAME
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                description,
                registration_mode,
                team_min_size,
                team_max_size,
                event_date,
                start_time,
                end_time,
                venue,
                status,
                registration_open,
                prizes,
                rules,
                requirements,
                certificate_enabled
            FROM games
            WHERE id = %s
            LIMIT 1
            """,
            (game_id,)
        )

        game = cursor.fetchone()

        if not game:
            flash("Event not found.", "error")
            return redirect(url_for("games.games"))

        # ----------------------------------------------------
        # CURRENT STUDENT
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                student_id,
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

        if not student:

            session.clear()

            return redirect(
                url_for("auth.login")
            )

        # ----------------------------------------------------
        # EXISTING REGISTRATION
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                registration_status,
                registered_at
            FROM registrations
            WHERE student_id = %s
              AND game_id = %s
            LIMIT 1
            """,
            (
                student["id"],
                game_id
            )
        )

        registration = cursor.fetchone()

        # ----------------------------------------------------
        # TEAM INFORMATION
        # ----------------------------------------------------

        teams = []

        if game["registration_mode"] == "TEAM":

            cursor.execute(
                """
                SELECT
                    t.id,
                    t.team_name,
                    t.team_leader_id,
                    t.status,
                    COUNT(tm.id) AS member_count
                FROM teams t
                LEFT JOIN team_members tm
                    ON tm.team_id = t.id
                WHERE t.game_id = %s
                GROUP BY
                    t.id,
                    t.team_name,
                    t.team_leader_id,
                    t.status
                ORDER BY t.team_name ASC
                """,
                (game_id,)
            )

            teams = cursor.fetchall()

        return render_template(
            "game_details.html",
            game=game,
            student=student,
            registration=registration,
            teams=teams
        )

    except Exception:

        if connection:
            connection.rollback()

        flash(
            "Unable to load event details right now.",
            "error"
        )

        return redirect(
            url_for("games.games")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# INDIVIDUAL REGISTRATION
# ============================================================

@games_bp.route(
    "/<int:game_id>/register",
    methods=["POST"]
)
@student_login_required
def register(game_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # STUDENT
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                student_id,
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

        if not student:

            session.clear()

            return redirect(
                url_for("auth.login")
            )

        # ----------------------------------------------------
        # EVENT
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                registration_mode,
                registration_open,
                status
            FROM games
            WHERE id = %s
            LIMIT 1
            """,
            (game_id,)
        )

        game = cursor.fetchone()

        if not game:

            flash(
                "Event not found.",
                "error"
            )

            return redirect(
                url_for("games.games")
            )

        # ----------------------------------------------------
        # REGISTRATION CHECK
        # ----------------------------------------------------

        if not game["registration_open"]:

            flash(
                "Registration for this event is currently closed.",
                "error"
            )

            return redirect(
                url_for(
                    "games.game_details",
                    game_id=game_id
                )
            )

        # ----------------------------------------------------
        # TEAM EVENTS
        # ----------------------------------------------------

        if game["registration_mode"] == "TEAM":

            flash(
                "This is a team event. Team registration will be handled through the team registration flow.",
                "info"
            )

            return redirect(
                url_for(
                    "games.game_details",
                    game_id=game_id
                )
            )

        # ----------------------------------------------------
        # DUPLICATE CHECK
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM registrations
            WHERE student_id = %s
              AND game_id = %s
            LIMIT 1
            """,
            (
                student["id"],
                game_id
            )
        )

        existing = cursor.fetchone()

        if existing:

            flash(
                "You are already registered for this event.",
                "info"
            )

            return redirect(
                url_for(
                    "games.game_details",
                    game_id=game_id
                )
            )

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO registrations
            (
                student_id,
                game_id,
                registration_status
            )
            VALUES
            (
                %s,
                %s,
                'REGISTERED'
            )
            """,
            (
                student["id"],
                game_id
            )
        )

        connection.commit()

        flash(
            f"Registration successful for {game['name']}.",
            "success"
        )

        return redirect(
            url_for(
                "games.game_details",
                game_id=game_id
            )
        )

    except Exception:

        if connection:
            connection.rollback()

        flash(
            "Registration could not be completed. Please try again.",
            "error"
        )

        return redirect(
            url_for(
                "games.game_details",
                game_id=game_id
            )
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# CANCEL REGISTRATION
# ============================================================

@games_bp.route(
    "/<int:game_id>/cancel",
    methods=["POST"]
)
@student_login_required
def cancel_registration(game_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE id = %s
              AND is_active = TRUE
            LIMIT 1
            """,
            (session["student_id"],)
        )

        student = cursor.fetchone()

        if not student:

            session.clear()

            return redirect(
                url_for("auth.login")
            )

        cursor.execute(
            """
            SELECT id
            FROM registrations
            WHERE student_id = %s
              AND game_id = %s
            LIMIT 1
            """,
            (
                student["id"],
                game_id
            )
        )

        registration = cursor.fetchone()

        if not registration:

            flash(
                "No registration was found.",
                "info"
            )

            return redirect(
                url_for(
                    "games.game_details",
                    game_id=game_id
                )
            )

        cursor.execute(
            """
            DELETE FROM registrations
            WHERE id = %s
              AND student_id = %s
            """,
            (
                registration["id"],
                student["id"]
            )
        )

        connection.commit()

        flash(
            "Registration cancelled successfully.",
            "success"
        )

        return redirect(
            url_for(
                "games.game_details",
                game_id=game_id
            )
        )

    except Exception:

        if connection:
            connection.rollback()

        flash(
            "Unable to cancel registration.",
            "error"
        )

        return redirect(
            url_for(
                "games.game_details",
                game_id=game_id
            )
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()