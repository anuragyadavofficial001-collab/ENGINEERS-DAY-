# ============================================================
# ENGINEERS DAY 2026
# STUDENT AUTHENTICATION
# ============================================================
# Direct Login using Admin-Saved Student Information
# OTP / AWS SES REMOVED
#
# Authentication source:
#     students table
#
# Login requires:
#     Student ID
#     Name
#     Phone
#     Email
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


# ============================================================
# BLUEPRINT
# ============================================================

auth_bp = Blueprint("auth", __name__)


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_name(name):
    """
    Normalize student name.

    Example:
        "Anurag   Yadav"
        ->
        "anurag yadav"
    """

    if not name:
        return ""

    name = " ".join(str(name).strip().split())

    return name.casefold()


def normalize_email(email):
    """
    Normalize email for comparison.
    """

    if not email:
        return ""

    return str(email).strip().casefold()


def normalize_phone(phone):
    """
    Normalize Indian mobile number.

    Accepted examples:

        9876543210
        919876543210
        +919876543210
        98765-43210
        98765 43210

    Internal format:

        919876543210
    """

    if phone is None:
        return ""

    phone = str(phone).strip()

    # Remove spaces, hyphens and brackets
    phone = re.sub(r"[\s\-()]+", "", phone)

    # +919876543210 -> 919876543210
    if phone.startswith("+91"):
        phone = phone[1:]

    # 919876543210
    if re.fullmatch(r"91[6-9]\d{9}", phone):
        return phone

    # 9876543210 -> 919876543210
    if re.fullmatch(r"[6-9]\d{9}", phone):
        return "91" + phone

    return ""


def normalize_student_id(student_id):
    """
    Normalize Student ID / Roll Number.
    """

    if student_id is None:
        return ""

    return str(student_id).strip().upper()


# ============================================================
# VALIDATION HELPERS
# ============================================================

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

    name = " ".join(
        str(name or "").strip().split()
    )

    if len(name) < 2 or len(name) > 100:
        return None

    # Supports:
    # Anurag Yadav
    # Anurag Kumar Yadav
    # O'Connor
    # A. Yadav

    if not re.fullmatch(
        r"[A-Za-z .'-]+",
        name
    ):
        return None

    return name


def validate_email(email):

    email = normalize_email(email)

    if not email:
        return None

    if len(email) > 150:
        return None

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

    if not re.fullmatch(
        r"91[6-9]\d{9}",
        phone
    ):
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

    # Already authenticated
    if (
        session.get("authenticated")
        and session.get("student_id")
    ):
        return redirect(
            url_for("student.home")
        )

    return render_template("login.html")


# ============================================================
# STUDENT LOGIN
# ============================================================

@auth_bp.route("/login", methods=["POST"])
def login_post():
    """
    Direct student authentication.

    Student must provide:

        Student ID
        Name
        Phone
        Email

    All four values must belong to the
    SAME active student record.
    """

    # ========================================================
    # GET FORM DATA
    # ========================================================

    student_id_raw = request.form.get(
        "student_id",
        ""
    )

    name_raw = request.form.get(
        "name",
        ""
    )

    phone_raw = request.form.get(
        "phone",
        ""
    )

    email_raw = request.form.get(
        "email",
        ""
    )


    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    student_id = validate_student_id(
        student_id_raw
    )

    name = validate_name(
        name_raw
    )

    phone = validate_phone(
        phone_raw
    )

    email = validate_email(
        email_raw
    )


    # --------------------------------------------------------
    # Student ID validation
    # --------------------------------------------------------

    if not student_id:

        flash(
            "Please enter a valid Student ID / Roll Number.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    # --------------------------------------------------------
    # Name validation
    # --------------------------------------------------------

    if not name:

        flash(
            "Please enter a valid student name.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    # --------------------------------------------------------
    # Phone validation
    # --------------------------------------------------------

    if not phone:

        flash(
            "Please enter a valid 10-digit mobile number.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    # --------------------------------------------------------
    # Email validation
    # --------------------------------------------------------

    if not email:

        flash(
            "Please enter a valid email address.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    # ========================================================
    # DATABASE
    # ========================================================

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        # ====================================================
        # FIND STUDENT
        # ====================================================
        #
        # We search ONLY by Student ID first.
        #
        # Then we compare:
        #
        #   Student ID
        #   Name
        #   Email
        #   Phone
        #
        # against the same database record.
        # ====================================================

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


        # ====================================================
        # STUDENT NOT FOUND
        # ====================================================

        if not student:

            flash(
                "Student information does not match our records.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        # ====================================================
        # ACCOUNT INACTIVE
        # ====================================================

        if not student.get("is_active"):

            flash(
                "Your student account is currently inactive. "
                "Please contact the administration.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        # ====================================================
        # NORMALIZE DATABASE VALUES
        # ====================================================

        db_student_id = normalize_student_id(
            student.get("student_id")
        )

        db_name = normalize_name(
            student.get("name")
        )

        db_email = normalize_email(
            student.get("email")
        )

        db_phone = normalize_phone(
            student.get("phone")
        )


        # ====================================================
        # NORMALIZE USER INPUT
        # ====================================================

        input_student_id = normalize_student_id(
            student_id
        )

        input_name = normalize_name(
            name
        )

        input_email = normalize_email(
            email
        )

        input_phone = normalize_phone(
            phone
        )


        # ====================================================
        # EXACT IDENTITY MATCH
        # ====================================================

        student_id_match = hmac.compare_digest(
            input_student_id,
            db_student_id
        )

        name_match = hmac.compare_digest(
            input_name,
            db_name
        )

        email_match = hmac.compare_digest(
            input_email,
            db_email
        )

        phone_match = hmac.compare_digest(
            input_phone,
            db_phone
        )


        # ====================================================
        # ALL FOUR MUST MATCH
        # ====================================================

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

            return redirect(
                url_for("auth.login")
            )


        # ====================================================
        # LOGIN SUCCESS
        # ====================================================

        # Destroy any old session data first
        session.clear()


        # Store internal database ID only
        session["student_id"] = student["id"]


        # Authentication flag
        session["authenticated"] = True


        # Permanent login session
        session.permanent = True


        # ====================================================
        # COMMIT
        # ====================================================

        connection.commit()


        # ====================================================
        # SUCCESS MESSAGE
        # ====================================================

        flash(
            f"Welcome, {student['name']}!",
            "success"
        )


        # ====================================================
        # REDIRECT TO STUDENT DASHBOARD
        # ====================================================

        return redirect(
            url_for("student.home")
        )


    # ========================================================
    # DATABASE / APPLICATION ERROR
    # ========================================================

    except Exception as error:

        # Rollback failed transaction
        if connection:

            try:
                connection.rollback()

            except Exception:
                pass


        # Print actual error in Flask terminal
        # This is extremely useful during development.
        print(
            "\n"
            "====================================================\n"
            "STUDENT LOGIN DATABASE ERROR\n"
            "===================================================="
        )

        print(
            repr(error)
        )

        print(
            "====================================================\n"
        )


        flash(
            "Unable to verify your information right now. "
            "Please try again.",
            "error"
        )


        return redirect(
            url_for("auth.login")
        )


    # ========================================================
    # CLEANUP
    # ========================================================

    finally:

        if cursor:

            try:
                cursor.close()

            except Exception:
                pass


        if connection:

            try:
                connection.close()

            except Exception:
                pass


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

    return redirect(
        url_for("auth.login")
    )