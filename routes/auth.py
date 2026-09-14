# ============================================================
# ENGINEERS DAY - STUDENT AUTHENTICATION
# Direct Login using Admin-Saved Student Information
# OTP / AWS SES REMOVED
# ============================================================

import re
import hmac

from functools import wraps
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from database.db import get_db_connection


auth_bp = Blueprint("auth", __name__)


# ============================================================
# VALIDATION HELPERS
# ============================================================

def normalize_name(name):
    """
    Normalize name for reliable comparison.
    Example:
        "Anurag   Yadav" -> "anurag yadav"
    """
    if not name:
        return ""

    name = " ".join(name.strip().split())
    return name.casefold()


def normalize_email(email):
    """
    Normalize email for exact comparison.
    """
    if not email:
        return ""

    return email.strip().casefold()


def normalize_phone(phone):
    """
    Normalize Indian phone number.

    Accepted:
        9876543210
        919876543210
        +919876543210
        98765-43210
        98765 43210
    """

    if not phone:
        return ""

    phone = phone.strip()
    phone = re.sub(r"[\s\-()]+", "", phone)

    if phone.startswith("+91"):
        phone = phone[1:]

    if phone.startswith("91") and len(phone) == 12:
        return phone

    if re.fullmatch(r"[6-9]\d{9}", phone):
        return "91" + phone

    return ""


def normalize_student_id(student_id):
    """
    Student ID / Roll Number normalization.
    """
    if not student_id:
        return ""

    return student_id.strip().upper()


def validate_student_id(student_id):
    student_id = normalize_student_id(student_id)

    if not student_id:
        return None

    if len(student_id) > 50:
        return None

    if not re.fullmatch(
        r"[A-Z0-9][A-Z0-9._/-]{0,49}",
        student_id
    ):
        return None

    return student_id


def validate_name(name):
    name = " ".join((name or "").strip().split())

    if len(name) < 2 or len(name) > 100:
        return None

    # Allows:
    # Anurag Yadav
    # Anurag Kumar Yadav
    # O'Connor
    # A. Yadav
    if not re.fullmatch(r"[A-Za-z .'-]+", name):
        return None

    return name


def validate_email(email):
    email = normalize_email(email)

    if not email:
        return None

    if len(email) > 150:
        return None

    # Practical email validation
    if not re.fullmatch(
        r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+",
        email
    ):
        return None

    return email


def validate_phone(phone):
    phone = normalize_phone(phone)

    if not phone:
        return None

    if not re.fullmatch(r"91[6-9]\d{9}", phone):
        return None

    return phone


# ============================================================
# LOGIN PAGE
# ============================================================

@auth_bp.route("/login", methods=["GET"])
def login():
    """
    Student login page.
    """

    # Already logged in
    if session.get("authenticated") and session.get("student_id"):
        return redirect(url_for("student.home"))

    return render_template("login.html")


# ============================================================
# STUDENT LOGIN
# ============================================================

@auth_bp.route("/login", methods=["POST"])
def login_post():
    """
    Direct student authentication.

    Student must provide the SAME information
    that Admin imported/saved in the database:

        Student ID
        Name
        Phone
        Email

    All four fields must match the same student record.
    """

    # --------------------------------------------------------
    # GET FORM DATA
    # --------------------------------------------------------

    student_id_raw = request.form.get("student_id", "")
    name_raw = request.form.get("name", "")
    phone_raw = request.form.get("phone", "")
    email_raw = request.form.get("email", "")

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    student_id = validate_student_id(student_id_raw)
    name = validate_name(name_raw)
    phone = validate_phone(phone_raw)
    email = validate_email(email_raw)

    if not student_id:
        flash("Please enter a valid Student ID / Roll Number.", "error")
        return redirect(url_for("auth.login"))

    if not name:
        flash("Please enter a valid student name.", "error")
        return redirect(url_for("auth.login"))

    if not phone:
        flash("Please enter a valid mobile number.", "error")
        return redirect(url_for("auth.login"))

    if not email:
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("auth.login"))

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # FIND STUDENT BY STUDENT ID
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
                year,
                is_active
            FROM students
            WHERE student_id = %s
            LIMIT 1
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        # ----------------------------------------------------
        # STUDENT NOT FOUND
        # ----------------------------------------------------

        if not student:
            flash(
                "Student information does not match our records.",
                "error"
            )
            return redirect(url_for("auth.login"))

        # ----------------------------------------------------
        # ACCOUNT DISABLED
        # ----------------------------------------------------

        if not student.get("is_active"):
            flash(
                "Your student account is currently inactive. "
                "Please contact the administration.",
                "error"
            )
            return redirect(url_for("auth.login"))

        # ----------------------------------------------------
        # NORMALIZE DATABASE VALUES
        # ----------------------------------------------------

        db_name = normalize_name(student.get("name"))
        db_email = normalize_email(student.get("email"))
        db_phone = normalize_phone(student.get("phone"))
        db_student_id = normalize_student_id(student.get("student_id"))

        # ----------------------------------------------------
        # EXACT IDENTITY MATCH
        # ----------------------------------------------------

        name_match = hmac.compare_digest(
            name.casefold(),
            db_name
        )

        email_match = hmac.compare_digest(
            email,
            db_email
        )

        phone_match = hmac.compare_digest(
            phone,
            db_phone
        )

        student_id_match = hmac.compare_digest(
            student_id,
            db_student_id
        )

        # ----------------------------------------------------
        # ALL FOUR MUST MATCH
        # ----------------------------------------------------

        if not (
            student_id_match
            and name_match
            and email_match
            and phone_match
        ):
            flash(
                "Student information does not match our records.",
                "error"
            )
            return redirect(url_for("auth.login"))

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        # Clear any old authentication/session state
        session.clear()

        # Store ONLY internal student DB ID
        session["student_id"] = student["id"]

        # Authentication flag
        session["authenticated"] = True

        # Persistent session
        session.permanent = True

        # ----------------------------------------------------
        # OPTIONAL REGISTRY CHECK
        # ----------------------------------------------------
        #
        # If student_registry exists, make sure the Student ID
        # is not disabled there.
        #
        # We intentionally do not require a registry record here
        # because students table is the actual account record.
        #

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    student_id,
                    is_active
                FROM student_registry
                WHERE student_id = %s
                LIMIT 1
                """,
                (student_id,)
            )

            registry_student = cursor.fetchone()

            if registry_student:
                if not registry_student.get("is_active"):
                    session.clear()

                    flash(
                        "Your Student ID is currently disabled "
                        "by the administration.",
                        "error"
                    )

                    return redirect(url_for("auth.login"))

        except Exception:
            # If registry table/query is unavailable,
            # don't break login for a valid students record.
            pass

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        connection.commit()

        flash(
            f"Welcome, {student['name']}!",
            "success"
        )

        return redirect(url_for("student.home"))

    except Exception:
        if connection:
            connection.rollback()

        flash(
            "Unable to verify your information right now. "
            "Please try again.",
            "error"
        )

        return redirect(url_for("auth.login"))

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route("/logout", methods=["GET"])
def logout():
    """
    Completely destroy student session.
    """

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("auth.login"))