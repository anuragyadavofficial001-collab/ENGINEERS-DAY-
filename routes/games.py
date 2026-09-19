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
            WHERE status IN ('UPCOMING', 'ONGOING')
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

    except Exception as error:

        if connection:
            connection.rollback()

        print("\n==============================================")
        print("STUDENT GAMES PAGE DATABASE ERROR")
        print("==============================================")
        print(repr(error))
        print("==============================================\n")

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
        # GAME DETAILS
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
            WHERE id = %s
            LIMIT 1
            """,
            (game_id,)
        )

        game = cursor.fetchone()

        # ----------------------------------------------------
        # IMPORTANT:
        # NEVER REDIRECT TO /games/ IF ID IS INVALID.
        # ----------------------------------------------------

        if not game:
            return (
                f"""
                <h2>Game not found</h2>
                <p>Game ID <strong>{game_id}</strong> does not exist.</p>
                <p>
                    <a href="{url_for('games.games')}">
                        Back to Events
                    </a>
                </p>
                """,
                404
            )

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
                student_id,
                game_id,
                status,
                registered_at,
                updated_at
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
                ORDER BY
                    t.team_name ASC
                """,
                (game_id,)
            )

            teams = cursor.fetchall()

        # ----------------------------------------------------
        # PUBLISHED RESULT
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                game_id,
                winner,
                winner_student_id,
                winner_team_id,
                runner_up,
                runner_up_student_id,
                runner_up_team_id,
                winner_prize,
                runner_up_prize,
                winner_certificate,
                runner_up_certificate,
                result_details,
                is_published,
                published_at
            FROM results
            WHERE game_id = %s
              AND is_published = TRUE
            ORDER BY
                published_at DESC NULLS LAST,
                id DESC
            LIMIT 1
            """,
            (game_id,)
        )

        result = cursor.fetchone()

        # ----------------------------------------------------
        # RENDER SAME CREATIVE PAGE FOR EVERY GAME
        # ----------------------------------------------------

        return render_template(
            "game_details.html",
            game=game,
            student=student,
            registration=registration,
            teams=teams,
            result=result
        )

    except Exception as error:

        if connection:
            connection.rollback()

        print("\n==============================================")
        print("GAME DETAILS DATABASE ERROR")
        print("==============================================")
        print(f"GAME ID: {game_id}")
        print(f"ERROR TYPE: {type(error).__name__}")
        print(f"ERROR: {repr(error)}")
        print("==============================================\n")

        # IMPORTANT:
        # Do NOT redirect to /games/
        # Otherwise every database/template error looks like
        # the user simply opened the events listing page.

        return (
            f"""
            <h2>Unable to load game details</h2>
            <p>
                Game ID:
                <strong>{game_id}</strong>
            </p>
            <p>
                Please check the Flask terminal for the exact error.
            </p>
            <p>
                <a href="{url_for('games.games')}">
                    Back to Events
                </a>
            </p>
            """,
            500
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
                game_name,
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
        # REGISTRATION OPEN CHECK
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
        # TEAM EVENT
        # ----------------------------------------------------

        if game["registration_mode"] == "TEAM":

            flash(
                "This is a team event. Team registration will be added through the team registration flow.",
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
            SELECT
                id,
                status
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

            # ------------------------------------------------
            # ALLOW RE-REGISTRATION AFTER CANCELLATION
            # ------------------------------------------------

            if existing["status"] == "CANCELLED":

                cursor.execute(
                    """
                    UPDATE registrations
                    SET
                        status = 'REGISTERED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND student_id = %s
                      AND game_id = %s
                    """,
                    (
                        existing["id"],
                        student["id"],
                        game_id
                    )
                )

                connection.commit()

                flash(
                    f"Registration successful for {game['game_name']}.",
                    "success"
                )

                return redirect(
                    url_for(
                        "games.game_details",
                        game_id=game_id
                    )
                )

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
        # INSERT REGISTRATION
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO registrations
            (
                student_id,
                game_id,
                status
            )
            VALUES
            (
                %s,
                %s,
                'REGISTERED'
            )
            RETURNING id
            """,
            (
                student["id"],
                game_id
            )
        )

        registration_row = cursor.fetchone()

        connection.commit()

        registration_id = (
            registration_row["id"]
            if registration_row
            else None
        )

        if registration_id:

            flash(
                f"Registration successful for {game['game_name']}. "
                f"Registration ID: {registration_id}",
                "success"
            )

        else:

            flash(
                f"Registration successful for {game['game_name']}.",
                "success"
            )

        return redirect(
            url_for(
                "games.game_details",
                game_id=game_id
            )
        )

    except Exception as error:

        if connection:
            connection.rollback()

        print("\n==============================================")
        print("REGISTRATION DATABASE ERROR")
        print("==============================================")
        print(f"GAME ID: {game_id}")
        print(f"ERROR TYPE: {type(error).__name__}")
        print(f"ERROR: {repr(error)}")
        print("==============================================\n")

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

        # ----------------------------------------------------
        # STUDENT
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id
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
        # REGISTRATION
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                status
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

        # ----------------------------------------------------
        # CANCEL
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE registrations
            SET
                status = 'CANCELLED',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND student_id = %s
              AND game_id = %s
            """,
            (
                registration["id"],
                student["id"],
                game_id
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

    except Exception as error:

        if connection:
            connection.rollback()

        print("\n==============================================")
        print("CANCEL REGISTRATION DATABASE ERROR")
        print("==============================================")
        print(f"GAME ID: {game_id}")
        print(f"ERROR TYPE: {type(error).__name__}")
        print(f"ERROR: {repr(error)}")
        print("==============================================\n")

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