# ============================================================
# ENGINEERS DAY - ADMIN MANAGEMENT
# Super Admin -> Game Admin Management
# ============================================================

from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from werkzeug.security import generate_password_hash

from database.db import get_db_connection


# ============================================================
# BLUEPRINT
# ============================================================

admin_management_bp = Blueprint(
    "admin_management",
    __name__,
    url_prefix="/admin/manage"
)


# ============================================================
# DATABASE HELPERS
# ============================================================

def rollback_db(connection):

    if connection:

        try:
            connection.rollback()

        except Exception:
            pass


def close_db(connection, cursor):

    try:

        if cursor:
            cursor.close()

    except Exception:
        pass

    try:

        if connection:
            connection.close()

    except Exception:
        pass


# ============================================================
# SUPER ADMIN AUTHORIZATION
# ============================================================

def super_admin_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        # ----------------------------------------------------
        # LOGIN CHECK
        # ----------------------------------------------------

        if not session.get("admin_authenticated"):

            return redirect(
                url_for("admin.login")
            )

        # ----------------------------------------------------
        # ROLE CHECK
        # ----------------------------------------------------

        if session.get("admin_role") != "SUPER_ADMIN":

            flash(
                "Only Super Admin can manage admin accounts.",
                "error"
            )

            return redirect(
                url_for("admin.dashboard")
            )

        return view_function(
            *args,
            **kwargs
        )

    return wrapped_view


# ============================================================
# CREATE GAME ADMIN
# ============================================================

@admin_management_bp.route(
    "/create-admin",
    methods=["GET", "POST"]
)
@super_admin_required
def create_admin():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # ====================================================
        # LOAD ALL GAMES
        # ====================================================

        cursor.execute(
            """
            SELECT
                id,
                game_name
            FROM games
            ORDER BY id ASC
            """
        )

        games = cursor.fetchall()

        # ====================================================
        # POST
        # ====================================================

        if request.method == "POST":

            full_name = request.form.get(
                "full_name",
                ""
            ).strip()

            username = request.form.get(
                "username",
                ""
            ).strip()

            password = request.form.get(
                "password",
                ""
            )

            raw_game_id = request.form.get(
                "game_id",
                ""
            ).strip()

            # ------------------------------------------------
            # BASIC VALIDATION
            # ------------------------------------------------

            if not full_name:

                flash(
                    "Full name is required.",
                    "error"
                )

                return render_template(
                    "admin/create_admin.html",
                    games=games
                )

            if not username:

                flash(
                    "Username is required.",
                    "error"
                )

                return render_template(
                    "admin/create_admin.html",
                    games=games
                )

            if not password:

                flash(
                    "Password is required.",
                    "error"
                )

                return render_template(
                    "admin/create_admin.html",
                    games=games
                )

            if len(password) < 8:

                flash(
                    "Password must be at least 8 characters.",
                    "error"
                )

                return render_template(
                    "admin/create_admin.html",
                    games=games
                )

            # ------------------------------------------------
            # GAME ID VALIDATION
            # ------------------------------------------------

            try:

                game_id = int(raw_game_id)

            except (TypeError, ValueError):

                flash(
                    "Please select a valid event.",
                    "error"
                )

                return render_template(
                    "admin/create_admin.html",
                    games=games
                )

            # ------------------------------------------------
            # VERIFY GAME EXISTS
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    id,
                    game_name
                FROM games
                WHERE id = %s
                LIMIT 1
                """,
                (game_id,)
            )

            selected_game = cursor.fetchone()

            if not selected_game:

                flash(
                    "Selected event was not found.",
                    "error"
                )

                return render_template(
                    "admin/create_admin.html",
                    games=games
                )

            # ------------------------------------------------
            # USERNAME DUPLICATE CHECK
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    id
                FROM admins
                WHERE LOWER(username) = LOWER(%s)
                LIMIT 1
                """,
                (username,)
            )

            existing_admin = cursor.fetchone()

            if existing_admin:

                flash(
                    "This username is already in use.",
                    "error"
                )

                return render_template(
                    "admin/create_admin.html",
                    games=games
                )

            # ------------------------------------------------
            # PASSWORD HASH
            # ------------------------------------------------

            password_hash = generate_password_hash(
                password
            )

            # ------------------------------------------------
            # CREATE GAME ADMIN
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO admins
                (
                    username,
                    full_name,
                    password_hash,
                    role,
                    game_id,
                    is_active,
                    created_by
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    'GAME_ADMIN',
                    %s,
                    TRUE,
                    %s
                )
                """,
                (
                    username,
                    full_name,
                    password_hash,
                    game_id,
                    session.get("admin_id")
                )
            )

            connection.commit()

            flash(
                "Game Admin created successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "admin_management.create_admin"
                )
            )

        # ====================================================
        # GET
        # ====================================================

        return render_template(
            "admin/create_admin.html",
            games=games
        )

    except Exception:

        rollback_db(
            connection
        )

        current_app.logger.exception(
            "Game Admin creation error"
        )

        flash(
            "Unable to create Game Admin right now.",
            "error"
        )

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    finally:

        close_db(
            connection,
            cursor
        )