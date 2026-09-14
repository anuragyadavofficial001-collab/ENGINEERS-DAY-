# ============================================================
# ENGINEERS DAY 2026 - ADMIN CONTROL CENTER
# ============================================================

import csv
import io
import os
import re
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

from openpyxl import load_workbook
from pypdf import PdfReader
from werkzeug.security import check_password_hash

from database.db import get_db_connection


# ============================================================
# BLUEPRINT
# ============================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ============================================================
# ADMIN AUTH
# ============================================================

def admin_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if not session.get("admin_authenticated"):
            return redirect(url_for("admin.login"))

        return view_function(*args, **kwargs)

    return wrapped_view


# ============================================================
# ADMIN LOGIN
# ============================================================

@admin_bp.route("/login", methods=["GET", "POST"])
def login():

    if session.get("admin_authenticated"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return render_template("admin/login.html")

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    password_hash,
                    is_active
                FROM admins
                WHERE username = %s
                LIMIT 1
                """,
                (username,)
            )

            admin = cursor.fetchone()

            if not admin:

                flash(
                    "Invalid admin credentials.",
                    "error"
                )

                return render_template("admin/login.html")

            if not admin["is_active"]:

                flash(
                    "This admin account is disabled.",
                    "error"
                )

                return render_template("admin/login.html")

            if not check_password_hash(
                admin["password_hash"],
                password
            ):

                flash(
                    "Invalid admin credentials.",
                    "error"
                )

                return render_template("admin/login.html")

            session.clear()

            session["admin_authenticated"] = True
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            session.permanent = True

            return redirect(url_for("admin.dashboard"))

        except Exception:

            if connection:
                connection.rollback()

            current_app.logger.exception(
                "Admin login error"
            )

            flash(
                "Unable to process login right now.",
                "error"
            )

            return render_template("admin/login.html")

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("admin/login.html")


# ============================================================
# LOGOUT
# ============================================================

@admin_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("admin.login"))


# ============================================================
# DASHBOARD
# ============================================================

@admin_bp.route("/dashboard")
@admin_required
def dashboard():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM student_registry
            WHERE is_active = TRUE
            """
        )

        total_students = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM students
            WHERE is_active = TRUE
            """
        )

        active_accounts = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM games
            """
        )

        total_events = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM registrations
            """
        )

        total_registrations = cursor.fetchone()["total"]

        return render_template(
            "admin/dashboard.html",
            total_students=total_students,
            active_accounts=active_accounts,
            total_events=total_events,
            total_registrations=total_registrations
        )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Admin dashboard error"
        )

        flash(
            "Unable to load admin dashboard.",
            "error"
        )

        return redirect(url_for("admin.login"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# STUDENT REGISTRY
#
# Search:
# ?q=student_id
# ?q=name
# ?q=email
# ?q=phone
#
# Registry + actual student profile are joined together.
# ============================================================

@admin_bp.route("/students")
@admin_required
def students():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        search = request.args.get(
            "q",
            ""
        ).strip()

        status = request.args.get(
            "status",
            "all"
        ).strip().lower()

        # ----------------------------------------------------
        # Base query
        # ----------------------------------------------------

        query = """
            SELECT
                sr.id AS registry_id,
                sr.student_id,
                sr.is_active AS registry_active,
                sr.claimed,
                sr.claimed_student_id,
                sr.imported_at,
                sr.claimed_at,

                s.id AS account_id,
                s.name,
                s.email,
                s.phone,
                s.branch,
                s.section,
                s.year,
                s.is_active AS account_active

            FROM student_registry sr

            LEFT JOIN students s
                ON s.id = sr.claimed_student_id
                OR s.student_id = sr.student_id
        """

        conditions = []
        params = []

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        if search:

            conditions.append(
                """
                (
                    sr.student_id LIKE %s
                    OR s.student_id LIKE %s
                    OR s.name LIKE %s
                    OR s.email LIKE %s
                    OR s.phone LIKE %s
                    OR s.branch LIKE %s
                    OR s.section LIKE %s
                )
                """
            )

            search_value = f"%{search}%"

            params.extend([
                search_value,
                search_value,
                search_value,
                search_value,
                search_value,
                search_value,
                search_value
            ])

        # ----------------------------------------------------
        # Status filter
        # ----------------------------------------------------

        if status == "active":

            conditions.append(
                "sr.is_active = TRUE"
            )

        elif status == "disabled":

            conditions.append(
                "sr.is_active = FALSE"
            )

        elif status == "claimed":

            conditions.append(
                "sr.claimed = TRUE"
            )

        elif status == "unclaimed":

            conditions.append(
                "sr.claimed = FALSE"
            )

        if conditions:

            query += " WHERE " + " AND ".join(
                conditions
            )

        query += """
            ORDER BY sr.id DESC
            LIMIT 1000
        """

        cursor.execute(
            query,
            tuple(params)
        )

        registry = cursor.fetchall()

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM student_registry
            """
        )

        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM student_registry
            WHERE is_active = TRUE
            """
        )

        active = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM student_registry
            WHERE claimed = TRUE
            """
        )

        claimed = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM student_registry
            WHERE claimed = FALSE
            """
        )

        unclaimed = cursor.fetchone()["total"]

        return render_template(
            "admin/students.html",
            registry=registry,
            total=total,
            active=active,
            claimed=claimed,
            unclaimed=unclaimed,
            search=search,
            status=status
        )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Student registry error"
        )

        flash(
            "Unable to load student registry.",
            "error"
        )

        return redirect(url_for("admin.dashboard"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# STUDENT DETAIL
# ============================================================

@admin_bp.route(
    "/students/<int:registry_id>/view"
)
@admin_required
def student_detail(registry_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                sr.id AS registry_id,
                sr.student_id,
                sr.is_active AS registry_active,
                sr.claimed,
                sr.claimed_student_id,
                sr.imported_at,
                sr.claimed_at,

                s.id AS account_id,
                s.student_id AS account_student_id,
                s.name,
                s.email,
                s.phone,
                s.branch,
                s.section,
                s.year,
                s.is_active AS account_active

            FROM student_registry sr

            LEFT JOIN students s
                ON s.id = sr.claimed_student_id
                OR s.student_id = sr.student_id

            WHERE sr.id = %s

            LIMIT 1
            """,
            (registry_id,)
        )

        student = cursor.fetchone()

        if not student:

            flash(
                "Student record not found.",
                "error"
            )

            return redirect(
                url_for("admin.students")
            )

        return render_template(
            "admin/student_detail.html",
            student=student
        )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Student detail error"
        )

        flash(
            "Unable to load student details.",
            "error"
        )

        return redirect(
            url_for("admin.students")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# FILE CONFIG
# ============================================================

ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".pdf"
}

MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# NORMALIZE STUDENT ID
# ============================================================

def normalize_student_id(value):

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.upper()

    if not re.fullmatch(
        r"[A-Z0-9][A-Z0-9._/-]{0,49}",
        value
    ):
        return None

    return value


# ============================================================
# NORMALIZE TEXT
# ============================================================

def clean_text(value):

    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


# ============================================================
# NORMALIZE PHONE
# ============================================================

def normalize_phone(value):

    value = clean_text(value)

    if not value:
        return None

    value = re.sub(
        r"[\s()-]",
        "",
        value
    )

    if value.startswith("+91"):
        value = value[3:]

    if value.startswith("91") and len(value) == 12:
        value = value[2:]

    if re.fullmatch(r"[6-9]\d{9}", value):
        return value

    return None


# ============================================================
# NORMALIZE HEADER
# ============================================================

def normalize_header(value):

    if value is None:
        return ""

    value = str(value).strip().lower()

    return re.sub(
        r"[^a-z0-9]",
        "",
        value
    )


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(headers, possible_names):

    normalized = {}

    for index, header in enumerate(headers):

        normalized[
            normalize_header(header)
        ] = index

    for name in possible_names:

        key = normalize_header(name)

        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# COLUMN ALIASES
# ============================================================

ID_COLUMNS = [
    "Student ID",
    "StudentID",
    "Roll Number",
    "Roll No",
    "Roll",
    "Enrollment Number",
    "Enrollment No",
    "Enrollment"
]

NAME_COLUMNS = [
    "Name",
    "Student Name",
    "Full Name"
]

EMAIL_COLUMNS = [
    "Email",
    "Email ID",
    "Email Address"
]

PHONE_COLUMNS = [
    "Phone",
    "Mobile",
    "Mobile Number",
    "Phone Number",
    "Contact"
]

BRANCH_COLUMNS = [
    "Branch",
    "Course",
    "Program",
    "Department"
]

SECTION_COLUMNS = [
    "Section",
    "Sec"
]

YEAR_COLUMNS = [
    "Year",
    "Academic Year",
    "Year of Study"
]


# ============================================================
# BUILD STUDENT RECORD
# ============================================================

def build_record(row, headers):

    id_column = find_column(
        headers,
        ID_COLUMNS
    )

    if id_column is None:
        return None

    student_id = normalize_student_id(
        row[id_column]
        if id_column < len(row)
        else None
    )

    if not student_id:
        return None

    name_column = find_column(
        headers,
        NAME_COLUMNS
    )

    email_column = find_column(
        headers,
        EMAIL_COLUMNS
    )

    phone_column = find_column(
        headers,
        PHONE_COLUMNS
    )

    branch_column = find_column(
        headers,
        BRANCH_COLUMNS
    )

    section_column = find_column(
        headers,
        SECTION_COLUMNS
    )

    year_column = find_column(
        headers,
        YEAR_COLUMNS
    )

    def get_value(column):
        if column is None:
            return None

        if column >= len(row):
            return None

        return clean_text(row[column])

    phone = normalize_phone(
        get_value(phone_column)
    )

    return {
        "student_id": student_id,
        "name": get_value(name_column),
        "email": get_value(email_column),
        "phone": phone,
        "branch": get_value(branch_column),
        "section": get_value(section_column),
        "year": get_value(year_column)
    }


# ============================================================
# EXTRACT CSV
# ============================================================

def extract_from_csv(file_bytes):

    text = file_bytes.decode(
        "utf-8-sig",
        errors="ignore"
    )

    reader = csv.reader(
        io.StringIO(text)
    )

    rows = list(reader)

    if not rows:
        return []

    headers = rows[0]

    if find_column(headers, ID_COLUMNS) is None:

        raise ValueError(
            "Student ID / Roll Number column not found."
        )

    results = []

    for row in rows[1:]:

        record = build_record(
            row,
            headers
        )

        if record:
            results.append(record)

    return results


# ============================================================
# EXTRACT XLSX
# ============================================================

def extract_from_excel(file_bytes):

    workbook = load_workbook(
        io.BytesIO(file_bytes),
        read_only=True,
        data_only=True
    )

    results = []

    try:

        for sheet in workbook.worksheets:

            rows = sheet.iter_rows(
                values_only=True
            )

            try:
                headers = list(next(rows))
            except StopIteration:
                continue

            if find_column(
                headers,
                ID_COLUMNS
            ) is None:

                continue

            for row in rows:

                row = list(row)

                record = build_record(
                    row,
                    headers
                )

                if record:
                    results.append(record)

    finally:

        workbook.close()

    if not results:

        raise ValueError(
            "No valid student records were found."
        )

    return results


# ============================================================
# EXTRACT PDF
#
# PDF is treated as ID-only because extracting structured
# columns like Email/Phone/Branch from arbitrary PDFs is
# unreliable.
# ============================================================

def extract_from_pdf(file_bytes):

    reader = PdfReader(
        io.BytesIO(file_bytes)
    )

    results = []

    for page in reader.pages:

        text = page.extract_text() or ""

        candidates = re.findall(
            r"\b[A-Z0-9][A-Z0-9._/-]{2,49}\b",
            text.upper()
        )

        for candidate in candidates:

            student_id = normalize_student_id(
                candidate
            )

            if student_id:

                results.append({
                    "student_id": student_id,
                    "name": None,
                    "email": None,
                    "phone": None,
                    "branch": None,
                    "section": None,
                    "year": None
                })

    return results


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_student_records(
    filename,
    file_bytes
):

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise ValueError(
            "Unsupported file format. "
            "Only CSV, XLSX and PDF are allowed."
        )

    if len(file_bytes) > MAX_FILE_SIZE:

        raise ValueError(
            "File size cannot exceed 10 MB."
        )

    if extension == ".csv":

        records = extract_from_csv(
            file_bytes
        )

    elif extension == ".xlsx":

        records = extract_from_excel(
            file_bytes
        )

    elif extension == ".pdf":

        records = extract_from_pdf(
            file_bytes
        )

    else:

        records = []

    # --------------------------------------------------------
    # Remove duplicate Student IDs
    # --------------------------------------------------------

    unique = {}

    for record in records:

        student_id = record["student_id"]

        if student_id not in unique:

            unique[student_id] = record

        else:

            # Prefer rows containing more information.
            old = unique[student_id]

            for field in [
                "name",
                "email",
                "phone",
                "branch",
                "section",
                "year"
            ]:

                if not old.get(field) and record.get(field):
                    old[field] = record[field]

    return list(unique.values())


# ============================================================
# SAVE STUDENT RECORD
#
# Registry = authorization
# Students  = profile/account
# ============================================================

def save_student_record(
    cursor,
    record
):

    student_id = record["student_id"]

    # --------------------------------------------------------
    # Check registry
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            claimed
        FROM student_registry
        WHERE student_id = %s
        LIMIT 1
        """,
        (student_id,)
    )

    registry = cursor.fetchone()

    if registry:

        registry_id = registry["id"]

    else:

        cursor.execute(
            """
            INSERT INTO student_registry
            (
                student_id,
                is_active,
                claimed
            )
            VALUES
            (
                %s,
                TRUE,
                FALSE
            )
            """,
            (student_id,)
        )

        registry_id = cursor.lastrowid

    # --------------------------------------------------------
    # Check student profile
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            id
        FROM students
        WHERE student_id = %s
        LIMIT 1
        """,
        (student_id,)
    )

    existing_student = cursor.fetchone()

    fields = {
        "name": record.get("name"),
        "email": record.get("email"),
        "phone": record.get("phone"),
        "branch": record.get("branch"),
        "section": record.get("section"),
        "year": record.get("year")
    }

    if existing_student:

        # ----------------------------------------------------
        # Update only values actually supplied by import.
        # ----------------------------------------------------

        updates = []
        values = []

        for field, value in fields.items():

            if value is not None:

                updates.append(
                    f"{field} = %s"
                )

                values.append(value)

        if updates:

            values.append(
                existing_student["id"]
            )

            cursor.execute(
                f"""
                UPDATE students
                SET {", ".join(updates)}
                WHERE id = %s
                """,
                tuple(values)
            )

        return "updated"

    # --------------------------------------------------------
    # New student profile
    # --------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO students
        (
            name,
            email,
            phone,
            student_id,
            branch,
            section,
            year,
            is_active
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            TRUE
        )
        """,
        (
            fields["name"] or "Pending Student",
            fields["email"],
            fields["phone"],
            student_id,
            fields["branch"],
            fields["section"],
            fields["year"]
        )
    )

    return "added"


# ============================================================
# UPLOAD STUDENTS
# ============================================================

@admin_bp.route(
    "/students/upload",
    methods=["GET", "POST"]
)
@admin_required
def upload_students():

    if request.method == "GET":

        return render_template(
            "admin/upload_students.html"
        )

    uploaded_file = request.files.get(
        "student_file"
    )

    if not uploaded_file:

        flash(
            "Please select a file.",
            "error"
        )

        return redirect(
            url_for("admin.upload_students")
        )

    filename = (
        uploaded_file.filename or ""
    ).strip()

    if not filename:

        flash(
            "Invalid file.",
            "error"
        )

        return redirect(
            url_for("admin.upload_students")
        )

    file_bytes = uploaded_file.read()

    if not file_bytes:

        flash(
            "The uploaded file is empty.",
            "error"
        )

        return redirect(
            url_for("admin.upload_students")
        )

    connection = None
    cursor = None

    try:

        records = extract_student_records(
            filename,
            file_bytes
        )

        if not records:

            flash(
                "No valid student records were found.",
                "error"
            )

            return redirect(
                url_for("admin.upload_students")
            )

        connection = get_db_connection()
        cursor = connection.cursor()

        added = 0
        updated = 0

        for record in records:

            result = save_student_record(
                cursor,
                record
            )

            if result == "added":
                added += 1

            elif result == "updated":
                updated += 1

        connection.commit()

        flash(
            f"Import successful — "
            f"{added} new students, "
            f"{updated} existing profiles updated.",
            "success"
        )

        return redirect(
            url_for("admin.students")
        )

    except ValueError as error:

        if connection:
            connection.rollback()

        flash(
            str(error),
            "error"
        )

        return redirect(
            url_for("admin.upload_students")
        )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Student import error"
        )

        flash(
            "Student import failed. "
            "Please check the file format and data.",
            "error"
        )

        return redirect(
            url_for("admin.upload_students")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# MANUAL IMPORT
# ============================================================

@admin_bp.route(
    "/students/import",
    methods=["POST"]
)
@admin_required
def import_students():

    raw_ids = request.form.get(
        "student_ids",
        ""
    )

    if not raw_ids:

        flash(
            "No student data available.",
            "error"
        )

        return redirect(
            url_for("admin.upload_students")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        added = 0
        duplicate = 0

        for value in raw_ids.splitlines():

            student_id = normalize_student_id(
                value
            )

            if not student_id:
                continue

            cursor.execute(
                """
                SELECT id
                FROM student_registry
                WHERE student_id = %s
                LIMIT 1
                """,
                (student_id,)
            )

            existing = cursor.fetchone()

            if existing:

                duplicate += 1
                continue

            cursor.execute(
                """
                INSERT INTO student_registry
                (
                    student_id,
                    is_active,
                    claimed
                )
                VALUES
                (
                    %s,
                    TRUE,
                    FALSE
                )
                """,
                (student_id,)
            )

            added += 1

        connection.commit()

        flash(
            f"Student IDs imported — "
            f"{added} added, "
            f"{duplicate} duplicates skipped.",
            "success"
        )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Manual student import error"
        )

        flash(
            "Student import failed.",
            "error"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("admin.students")
    )


# ============================================================
# TOGGLE STUDENT
# ============================================================

# ============================================================
# TOGGLE STUDENT
# ============================================================

@admin_bp.route(
    "/students/<int:registry_id>/toggle",
    methods=["POST"]
)
@admin_required
def toggle_student(registry_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # Get registry record + linked student
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                sr.id,
                sr.student_id,
                sr.is_active,
                s.id AS account_id
            FROM student_registry sr

            LEFT JOIN students s
                ON s.student_id = sr.student_id

            WHERE sr.id = %s
            LIMIT 1
            """,
            (registry_id,)
        )

        student = cursor.fetchone()

        if not student:

            flash(
                "Student record not found.",
                "error"
            )

            return redirect(
                url_for("admin.students")
            )

        # ----------------------------------------------------
        # Calculate new status
        # ----------------------------------------------------

        new_status = not bool(
            student["is_active"]
        )

        # ----------------------------------------------------
        # Update registry
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE student_registry
            SET is_active = %s
            WHERE id = %s
            """,
            (
                new_status,
                registry_id
            )
        )

        # ----------------------------------------------------
        # Keep actual student account synchronized
        # ----------------------------------------------------

        if student["account_id"]:

            cursor.execute(
                """
                UPDATE students
                SET is_active = %s
                WHERE id = %s
                """,
                (
                    new_status,
                    student["account_id"]
                )
            )

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        connection.commit()

        if new_status:

            flash(
                f"{student['student_id']} has been enabled.",
                "success"
            )

        else:

            flash(
                f"{student['student_id']} has been disabled.",
                "success"
            )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Student toggle error"
        )

        flash(
            "Unable to update student status.",
            "error"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("admin.students")
    )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                student_id,
                is_active
            FROM student_registry
            WHERE id = %s
            LIMIT 1
            """,
            (registry_id,)
        )

        student = cursor.fetchone()

        if not student:

            flash(
                "Student record not found.",
                "error"
            )

            return redirect(
                url_for("admin.students")
            )

        cursor.execute(
            """
            UPDATE student_registry
            SET is_active = NOT is_active
            WHERE id = %s
            """,
            (registry_id,)
        )

        connection.commit()

        if student["is_active"]:

            flash(
                f"{student['student_id']} has been disabled.",
                "success"
            )

        else:

            flash(
                f"{student['student_id']} has been enabled.",
                "success"
            )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Student toggle error"
        )

        flash(
            "Unable to update student status.",
            "error"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("admin.students")
    )


# ============================================================
# DELETE STUDENT
#
# Only UNCLAIMED registry records can be directly deleted.
# ============================================================

@admin_bp.route(
    "/students/<int:registry_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_student(registry_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                student_id,
                claimed,
                claimed_student_id
            FROM student_registry
            WHERE id = %s
            LIMIT 1
            """,
            (registry_id,)
        )

        student = cursor.fetchone()

        if not student:

            flash(
                "Student record not found.",
                "error"
            )

            return redirect(
                url_for("admin.students")
            )

        if student["claimed"]:

            flash(
                f"{student['student_id']} is already claimed. "
                f"Disable it instead of deleting it.",
                "error"
            )

            return redirect(
                url_for("admin.students")
            )

        cursor.execute(
            """
            DELETE FROM student_registry
            WHERE id = %s
            AND claimed = FALSE
            """,
            (registry_id,)
        )

        connection.commit()

        flash(
            f"Student ID {student['student_id']} "
            f"was deleted successfully.",
            "success"
        )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Student deletion error"
        )

        flash(
            "Unable to delete student record.",
            "error"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
            # ============================================================
# EVENT MANAGEMENT
# ============================================================

@admin_bp.route("/events")
@admin_required
def events():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                game_name,
                description,
                registration_mode,
                team_min_size,
                team_max_size,
                event_date AS event_date,
                start_time AS start_time,
                CONCAT_WS(', ', block, floor, room) AS venue,
                prize_pool,
                rules,
                requirements,
                registration_open,
                status,
                winner_certificate,
                runner_up_certificate
            FROM games
            ORDER BY id ASC
        """)

        games = cursor.fetchall()

        return render_template(
            "admin/events.html",
            games=games
        )

    except Exception as e:
        if connection:
            connection.rollback()

        return f"Event management error: {e}"

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@admin_bp.route("/events/<int:game_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_event(game_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # GET EVENT
        # ----------------------------------------------------

        cursor.execute("""
            SELECT *
            FROM games
            WHERE id = %s
            LIMIT 1
        """, (game_id,))

        game = cursor.fetchone()

        if not game:
            return "Event not found.", 404

        # ----------------------------------------------------
        # UPDATE EVENT
        # ----------------------------------------------------

        if request.method == "POST":

            game_name = request.form.get("game_name", "").strip()
            description = request.form.get("description", "").strip()
            registration_mode = request.form.get(
                "registration_mode",
                "INDIVIDUAL"
            )

            team_min_size = request.form.get(
                "team_min_size",
                "0"
            )

            team_max_size = request.form.get(
                "team_max_size",
                "0"
            )

            event_date = request.form.get(
                "event_date"
            ) or None

            start_time = request.form.get(
                "start_time"
            ) or None
            end_time = request.form.get(
                "end_time"
                ) or None
            block = request.form.get("block", "").strip()

            floor = request.form.get("floor", "").strip()

            room = request.form.get("room", "").strip()
            prize_pool = request.form.get(
                "prize_pool",
                ""
            ).strip()

            rules = request.form.get(
                "rules",
                ""
            ).strip()

            requirements = request.form.get(
                "requirements",
                ""
            ).strip()

            registration_open = (
                1
                if request.form.get("registration_open")
                else 0
            )

            status = request.form.get(
                "status",
                "UPCOMING"
            )

            winner_certificate = (
                1
                if request.form.get("winner_certificate")
                else 0
            )

            runner_up_certificate = (
                1
                if request.form.get("runner_up_certificate")
                else 0
            )

            # ------------------------------------------------
            # VALIDATION
            # ------------------------------------------------

            if not game_name:
                return "Event name is required.", 400

            if registration_mode not in (
                "INDIVIDUAL",
                "TEAM"
            ):
                return "Invalid registration mode.", 400

            try:
                team_min_size = int(team_min_size)
                team_max_size = int(team_max_size)
            except ValueError:
                return "Invalid team size.", 400

            if registration_mode == "INDIVIDUAL":
                team_min_size = 0
                team_max_size = 0

            else:
                if team_min_size < 1:
                    return "Team minimum size must be at least 1.", 400

                if team_max_size < team_min_size:
                    return "Maximum team size cannot be smaller than minimum.", 400

            # ------------------------------------------------
            # UPDATE DATABASE
            # ------------------------------------------------

            cursor.execute("""
                UPDATE games
                SET
                    game_name = %s,
                    description = %s,
                    registration_mode = %s,
                    team_min_size = %s,
                    team_max_size = %s,
                    event_date = %s,
                    start_time = %s,
                    end_time = %s,
                    block = %s,
                    floor = %s,
                    room = %s,
                    prize_pool = %s,
                    rules = %s,
                    requirements = %s,
                    registration_open = %s,
                    status = %s,
                    winner_certificate = %s,
                    runner_up_certificate = %s
                WHERE id = %s
            """, (
                game_name,
                description,
                registration_mode,
                team_min_size,
                team_max_size,
                event_date,
                start_time,
                end_time,
                block,
                floor,
                room,
                prize_pool,
                rules,
                requirements,
                registration_open,
                status,
                winner_certificate,
                runner_up_certificate,
                game_id
            ))

            connection.commit()

            return redirect(
                url_for("admin.events")
            )

        # ----------------------------------------------------
        # DISPLAY EDIT PAGE
        # ----------------------------------------------------

        return render_template(
            "admin/event_edit.html",
            game=game
        )

    except Exception:

        if connection:
            connection.rollback()

        return "Unable to update event.", 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("admin.students")
    )
# ============================================================
# REGISTRATION MANAGEMENT
# ============================================================

@admin_bp.route("/registrations")
@admin_required
def registrations():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        search = request.args.get("q", "").strip()
        status = request.args.get("status", "all").strip().upper()
        game_id = request.args.get("game_id", "").strip()

        query = """
            SELECT
                r.id,
                r.student_id,
                r.game_id,
                r.status,
                r.registered_at,
                r.updated_at,
                s.name AS student_name,
                s.student_id AS student_roll,
                s.email AS student_email,
                s.phone AS student_phone,
                s.branch,
                s.section,
                s.year,
                g.game_name,
                g.registration_mode,
                g.event_date,
                g.start_time,
                CONCAT_WS(', ', g.block, g.floor, g.room) AS venue
            FROM registrations r
            INNER JOIN students s ON s.id = r.student_id
            INNER JOIN games g ON g.id = r.game_id
        """

        conditions = []
        params = []

        if search:
            value = f"%{search}%"
            conditions.append("""
                (
                    s.name LIKE %s
                    OR s.student_id LIKE %s
                    OR s.email LIKE %s
                    OR s.phone LIKE %s
                    OR g.game_name LIKE %s
                )
            """)
            params.extend([value, value, value, value, value])

        if status in ("REGISTERED", "CANCELLED", "APPROVED", "REJECTED"):
            conditions.append("r.status = %s")
            params.append(status)

        if game_id.isdigit():
            conditions.append("r.game_id = %s")
            params.append(int(game_id))

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY r.registered_at DESC, r.id DESC LIMIT 2000"

        cursor.execute(query, tuple(params))
        registration_rows = cursor.fetchall()

        cursor.execute("""
            SELECT id, game_name
            FROM games
            ORDER BY game_name ASC
        """)
        games = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM registrations")
        total = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM registrations
            WHERE status = 'REGISTERED'
        """)
        registered = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM registrations
            WHERE status = 'APPROVED'
        """)
        approved = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM registrations
            WHERE status = 'CANCELLED'
        """)
        cancelled = cursor.fetchone()["total"]

        return render_template(
            "admin/registrations.html",
            registrations=registration_rows,
            games=games,
            total=total,
            registered=registered,
            approved=approved,
            cancelled=cancelled,
            search=search,
            status=status,
            selected_game_id=game_id
        )

    except Exception:
        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Admin registrations error"
        )

        flash(
            "Unable to load registrations.",
            "error"
        )

        return redirect(url_for("admin.dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# REGISTRATION DETAILS
# ============================================================

@admin_bp.route("/registrations/<int:registration_id>")
@admin_required
def registration_details(registration_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                r.id,
                r.student_id,
                r.game_id,
                r.status,
                r.registered_at,
                r.updated_at,

                s.name AS student_name,
                s.student_id AS student_roll,
                s.email AS student_email,
                s.phone AS student_phone,
                s.branch,
                s.section,
                s.year,

                g.game_name,
                g.description,
                g.registration_mode,
                g.team_min_size,
                g.team_max_size,
                g.event_date,
                g.start_time,
                CONCAT_WS(', ', g.block, g.floor, g.room) AS venue,
                g.prize_pool,
                g.rules,
                g.requirements,
                g.registration_open,
                g.status AS game_status

            FROM registrations r

            INNER JOIN students s
                ON s.id = r.student_id

            INNER JOIN games g
                ON g.id = r.game_id

            WHERE r.id = %s
            LIMIT 1
        """, (registration_id,))

        registration = cursor.fetchone()

        if not registration:
            flash(
                "Registration not found.",
                "error"
            )
            return redirect(url_for("admin.registrations"))

        return render_template(
            "admin/registration_details.html",
            registration=registration
        )

    except Exception:
        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Registration details error"
        )

        flash(
            "Unable to load registration details.",
            "error"
        )

        return redirect(url_for("admin.registrations"))

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# REGISTRATION STATUS UPDATE
#
# This endpoint is intentionally simple and server-side
# validated. It is useful for admin actions from the details
# page or future AJAX controls.
# ============================================================

@admin_bp.route(
    "/registrations/<int:registration_id>/status",
    methods=["POST"]
)
@admin_required
def update_registration_status(registration_id):

    new_status = request.form.get(
        "status",
        ""
    ).strip().upper()

    allowed = {
        "REGISTERED",
        "CANCELLED",
        "APPROVED",
        "REJECTED"
    }

    if new_status not in allowed:
        flash(
            "Invalid registration status.",
            "error"
        )
        return redirect(
            url_for(
                "admin.registration_details",
                registration_id=registration_id
            )
        )

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id
            FROM registrations
            WHERE id = %s
            LIMIT 1
        """, (registration_id,))

        if not cursor.fetchone():
            flash(
                "Registration not found.",
                "error"
            )
            return redirect(
                url_for("admin.registrations")
            )

        cursor.execute("""
            UPDATE registrations
            SET status = %s
            WHERE id = %s
        """, (new_status, registration_id))

        connection.commit()

        flash(
            f"Registration status changed to {new_status}.",
            "success"
        )

    except Exception:
        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Registration status update error"
        )

        flash(
            "Unable to update registration status.",
            "error"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for(
            "admin.registration_details",
            registration_id=registration_id
        )
    )



# ============================================================
# RESULTS MANAGEMENT
# ============================================================

@admin_bp.route("/results")
@admin_required
def results():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # FILTERS
        # ----------------------------------------------------

        selected_game_id = request.args.get(
            "game_id",
            ""
        ).strip()

        selected_status = request.args.get(
            "status",
            ""
        ).strip().lower()

        # ----------------------------------------------------
        # MAIN QUERY
        #
        # LEFT JOIN keeps events visible even when a result
        # has not been created yet.
        # ----------------------------------------------------

        query = """
            SELECT

                g.id AS game_id,
                g.game_name,
                g.registration_mode,
                g.event_date,
                g.start_time,
                g.end_time,
                g.block,
                g.floor,
                g.room,
                g.status AS game_status,

                r.id AS result_id,
                r.winner,
                r.runner_up,
                r.winner_prize,
                r.runner_up_prize,
                r.winner_certificate,
                r.runner_up_certificate,
                r.result_details,
                r.created_at

            FROM games g

            LEFT JOIN results r
                ON r.game_id = g.id
        """

        conditions = []
        params = []

        # ----------------------------------------------------
        # EVENT FILTER
        # ----------------------------------------------------

        if selected_game_id:

            try:

                game_id_value = int(
                    selected_game_id
                )

                conditions.append(
                    "g.id = %s"
                )

                params.append(
                    game_id_value
                )

            except ValueError:

                selected_game_id = ""

        # ----------------------------------------------------
        # RESULT STATUS FILTER
        #
        # "published" = result exists
        # "pending"   = event has no result yet
        # ----------------------------------------------------

        if selected_status == "published":

            conditions.append(
                "r.id IS NOT NULL"
            )

        elif selected_status == "pending":

            conditions.append(
                "r.id IS NULL"
            )

        # ----------------------------------------------------
        # WHERE
        # ----------------------------------------------------

        if conditions:

            query += """
                WHERE
            """

            query += " AND ".join(
                conditions
            )

        # ----------------------------------------------------
        # ORDER
        # ----------------------------------------------------

        query += """
            ORDER BY

                CASE
                    WHEN g.event_date IS NULL THEN 1
                    ELSE 0
                END ASC,

                g.event_date ASC,

                CASE
                    WHEN g.start_time IS NULL THEN 1
                    ELSE 0
                END ASC,

                g.start_time ASC,

                g.id ASC
        """

        cursor.execute(
            query,
            tuple(params)
        )

        results = cursor.fetchall()

        # ----------------------------------------------------
        # EVENTS FOR FILTER
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                game_name
            FROM games
            ORDER BY
                game_name ASC
            """
        )

        games = cursor.fetchall()

        # ----------------------------------------------------
        # OVERALL RESULT STATISTICS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM results
            """
        )

        total_results = cursor.fetchone()["total"]

        # ----------------------------------------------------
        # EVENTS WITH RESULTS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(DISTINCT game_id) AS total
            FROM results
            """
        )

        completed_events = cursor.fetchone()["total"]

        # ----------------------------------------------------
        # EVENTS WITHOUT RESULTS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM games g
            LEFT JOIN results r
                ON r.game_id = g.id
            WHERE r.id IS NULL
            """
        )

        pending_events = cursor.fetchone()["total"]

        # ----------------------------------------------------
        # TOTAL EVENTS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM games
            """
        )

        total_events = cursor.fetchone()["total"]

        # ----------------------------------------------------
        # RENDER
        # ----------------------------------------------------

        return render_template(
            "admin/results.html",

            results=results,
            games=games,

            total_results=total_results,
            completed_events=completed_events,
            pending_events=pending_events,
            total_events=total_events,

            selected_game_id=selected_game_id,
            selected_status=selected_status
        )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Admin results error"
        )

        flash(
            "Unable to load results management.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# CREATE RESULT
# ============================================================

@admin_bp.route(
    "/results/create",
    methods=["GET", "POST"]
)
@admin_required
def result_create():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if request.method == "POST":

            raw_game_id = request.form.get(
                "game_id",
                ""
            ).strip()

            try:
                game_id = int(raw_game_id)
            except (TypeError, ValueError):
                flash(
                    "Please select a valid event.",
                    "error"
                )
                return redirect(
                    url_for("admin.result_create")
                )

            cursor.execute("""
                SELECT
                    id,
                    game_name,
                    registration_mode
                FROM games
                WHERE id = %s
                LIMIT 1
            """, (game_id,))

            game = cursor.fetchone()

            if not game:
                flash(
                    "Event not found.",
                    "error"
                )
                return redirect(
                    url_for("admin.result_create")
                )

            winner = request.form.get(
                "winner",
                ""
            ).strip() or None

            runner_up = request.form.get(
                "runner_up",
                ""
            ).strip() or None

            winner_student_id = request.form.get(
                "winner_student_id",
                ""
            ).strip() or None

            winner_team_id = request.form.get(
                "winner_team_id",
                ""
            ).strip() or None

            runner_up_student_id = request.form.get(
                "runner_up_student_id",
                ""
            ).strip() or None

            runner_up_team_id = request.form.get(
                "runner_up_team_id",
                ""
            ).strip() or None

            winner_prize = request.form.get(
                "winner_prize",
                ""
            ).strip() or None

            runner_up_prize = request.form.get(
                "runner_up_prize",
                ""
            ).strip() or None

            winner_certificate = (
                1 if request.form.get("winner_certificate")
                else 0
            )

            runner_up_certificate = (
                1 if request.form.get("runner_up_certificate")
                else 0
            )

            result_details = request.form.get(
                "result_details",
                ""
            ).strip() or None

            is_published = (
                1 if request.form.get("is_published")
                else 0
            )

            published_at = (
                "NOW()" if is_published else None
            )

            cursor.execute("""
                SELECT id
                FROM results
                WHERE game_id = %s
                LIMIT 1
            """, (game_id,))

            existing = cursor.fetchone()

            if existing:
                flash(
                    "A result already exists for this event. "
                    "Use Edit instead.",
                    "error"
                )
                return redirect(
                    url_for(
                        "admin.result_edit",
                        game_id=game_id
                    )
                )

            if is_published:
                cursor.execute("""
                    INSERT INTO results
                    (
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
                        published_at,
                        published_by
                    )
                    VALUES
                    (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        NOW(), %s
                    )
                """, (
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
                    session.get("admin_id")
                ))
            else:
                cursor.execute("""
                    INSERT INTO results
                    (
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
                        published_at,
                        published_by
                    )
                    VALUES
                    (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        NULL, NULL
                    )
                """, (
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
                    is_published
                ))

            connection.commit()

            flash(
                "Result created successfully.",
                "success"
            )

            return redirect(
                url_for("admin.results")
            )

        cursor.execute("""
            SELECT
                g.id,
                g.game_name,
                g.registration_mode,
                g.event_date
            FROM games g
            LEFT JOIN results r
                ON r.game_id = g.id
            WHERE r.id IS NULL
            ORDER BY
                CASE WHEN g.event_date IS NULL THEN 1 ELSE 0 END,
                g.event_date ASC,
                g.game_name ASC
        """)

        games = cursor.fetchall()

        return render_template(
            "admin/result_edit.html",
            game=None,
            result=None,
            games=games,
            mode="create"
        )

    except Exception:
        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Result creation error"
        )

        flash(
            "Unable to create result.",
            "error"
        )

        return redirect(
            url_for("admin.results")
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# EDIT RESULT
# ============================================================

@admin_bp.route(
    "/results/<int:game_id>/edit",
    methods=["GET", "POST"]
)
@admin_required
def result_edit(game_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # --------------------------------------------------------
        # LOAD EVENT
        # --------------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                game_name,
                registration_mode,
                event_date
            FROM games
            WHERE id = %s
            LIMIT 1
        """, (game_id,))

        game = cursor.fetchone()

        if not game:
            flash("Event not found.", "error")
            return redirect(url_for("admin.results"))

        # --------------------------------------------------------
        # POST
        # --------------------------------------------------------

        if request.method == "POST":

            winner = (
                request.form.get("winner", "").strip()
                or None
            )

            runner_up = (
                request.form.get("runner_up", "").strip()
                or None
            )

            # ----------------------------------------------------
            # STUDENT / TEAM IDs
            # ----------------------------------------------------

            def clean_int(value):
                value = (value or "").strip()

                if not value:
                    return None

                try:
                    return int(value)
                except (TypeError, ValueError):
                    return None

            winner_student_id = clean_int(
                request.form.get("winner_student_id")
            )

            winner_team_id = clean_int(
                request.form.get("winner_team_id")
            )

            runner_up_student_id = clean_int(
                request.form.get("runner_up_student_id")
            )

            runner_up_team_id = clean_int(
                request.form.get("runner_up_team_id")
            )

            # ----------------------------------------------------
            # PRIZES
            # ----------------------------------------------------

            winner_prize = (
                request.form.get("winner_prize", "").strip()
                or None
            )

            runner_up_prize = (
                request.form.get("runner_up_prize", "").strip()
                or None
            )

            # ----------------------------------------------------
            # CERTIFICATES
            # ----------------------------------------------------

            winner_certificate = (
                1
                if request.form.get("winner_certificate")
                else 0
            )

            runner_up_certificate = (
                1
                if request.form.get("runner_up_certificate")
                else 0
            )

            # ----------------------------------------------------
            # DETAILS
            # ----------------------------------------------------

            result_details = (
                request.form.get("result_details", "").strip()
                or None
            )

            # ----------------------------------------------------
            # PUBLICATION
            # ----------------------------------------------------

            is_published = (
                1
                if request.form.get("is_published")
                else 0
            )

            # ----------------------------------------------------
            # CHECK RESULT EXISTS
            # ----------------------------------------------------

            cursor.execute("""
                SELECT id
                FROM results
                WHERE game_id = %s
                LIMIT 1
            """, (game_id,))

            existing_result = cursor.fetchone()

            if not existing_result:
                flash(
                    "No result exists for this event.",
                    "error"
                )

                return redirect(
                    url_for("admin.results")
                )

            # ----------------------------------------------------
            # PUBLISHED RESULT
            # ----------------------------------------------------

            if is_published:

                cursor.execute("""
                    UPDATE results
                    SET
                        winner = %s,
                        winner_student_id = %s,
                        winner_team_id = %s,

                        runner_up = %s,
                        runner_up_student_id = %s,
                        runner_up_team_id = %s,

                        winner_prize = %s,
                        runner_up_prize = %s,

                        winner_certificate = %s,
                        runner_up_certificate = %s,

                        result_details = %s,

                        is_published = 1,

                        published_at = COALESCE(
                            published_at,
                            NOW()
                        ),

                        published_by = %s

                    WHERE game_id = %s
                """, (
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

                    session.get("admin_id"),

                    game_id
                ))

            # ----------------------------------------------------
            # SAVE AS DRAFT
            # ----------------------------------------------------

            else:

                cursor.execute("""
                    UPDATE results
                    SET
                        winner = %s,
                        winner_student_id = %s,
                        winner_team_id = %s,

                        runner_up = %s,
                        runner_up_student_id = %s,
                        runner_up_team_id = %s,

                        winner_prize = %s,
                        runner_up_prize = %s,

                        winner_certificate = %s,
                        runner_up_certificate = %s,

                        result_details = %s,

                        is_published = 0,
                        published_at = NULL,
                        published_by = NULL

                    WHERE game_id = %s
                """, (
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

                    game_id
                ))

            # ----------------------------------------------------
            # COMMIT
            # ----------------------------------------------------

            connection.commit()

            if is_published:
                flash(
                    "Result published successfully.",
                    "success"
                )
            else:
                flash(
                    "Result saved as draft.",
                    "success"
                )

            return redirect(
                url_for("admin.results")
            )

        # --------------------------------------------------------
        # GET → LOAD RESULT
        # --------------------------------------------------------

        cursor.execute("""
            SELECT *
            FROM results
            WHERE game_id = %s
            LIMIT 1
        """, (game_id,))

        result = cursor.fetchone()

        if not result:
            flash(
                "No result exists for this event yet.",
                "error"
            )

            return redirect(
                url_for("admin.result_create", game_id=game_id)
            )

        # --------------------------------------------------------
        # RENDER
        # --------------------------------------------------------

        return render_template(
            "admin/result_edit.html",
            game=game,
            result=result,
            games=None,
            mode="edit"
        )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Result edit error"
        )

        flash(
            "Unable to update result.",
            "error"
        )

        return redirect(
            url_for("admin.results")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
# ============================================================
# NOTIFICATION MANAGEMENT
# ============================================================

@admin_bp.route("/notifications")
@admin_required
def notifications():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        search = request.args.get(
            "q",
            ""
        ).strip()

        notification_type = request.args.get(
            "type",
            "all"
        ).strip().upper()

        query = """
            SELECT
                n.id,
                n.game_id,
                n.title,
                n.message,
                n.notification_type,
                n.is_published,
                n.published_at,
                n.expires_at,
                n.created_by,
                n.created_at,
                n.updated_at,
                g.game_name
            FROM notifications n
            LEFT JOIN games g
                ON g.id = n.game_id
        """

        conditions = []
        params = []

        if search:
            value = f"%{search}%"
            conditions.append("""
                (
                    n.title LIKE %s
                    OR n.message LIKE %s
                    OR g.game_name LIKE %s
                )
            """)
            params.extend([value, value, value])

        allowed_types = {
            "GENERAL",
            "EVENT",
            "RESULT",
            "IMPORTANT"
        }

        if notification_type in allowed_types:
            conditions.append(
                "n.notification_type = %s"
            )
            params.append(notification_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
            ORDER BY n.created_at DESC, n.id DESC
            LIMIT 1000
        """

        cursor.execute(query, tuple(params))
        notification_rows = cursor.fetchall()

        cursor.execute("""
            SELECT
                id,
                game_name
            FROM games
            ORDER BY game_name ASC
        """)

        games = cursor.fetchall()

        return render_template(
            "admin/notifications.html",
            notifications=notification_rows,
            games=games,
            search=search,
            notification_type=notification_type
        )

    except Exception:
        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Admin notifications error"
        )

        flash(
            "Unable to load notifications.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# CREATE NOTIFICATION
# ============================================================

@admin_bp.route(
    "/notifications/create",
    methods=["GET", "POST"]
)
@admin_required
def notification_create():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if request.method == "POST":

            title = request.form.get(
                "title",
                ""
            ).strip()

            message = request.form.get(
                "message",
                ""
            ).strip()

            notification_type = request.form.get(
                "notification_type",
                "GENERAL"
            ).strip().upper()

            raw_game_id = request.form.get(
                "game_id",
                ""
            ).strip()

            game_id = (
                int(raw_game_id)
                if raw_game_id.isdigit()
                else None
            )

            expires_at = request.form.get(
                "expires_at",
                ""
            ).strip() or None

            is_published = (
                1 if request.form.get("is_published")
                else 0
            )

            allowed_types = {
                "GENERAL",
                "EVENT",
                "RESULT",
                "IMPORTANT"
            }

            if not title:
                flash(
                    "Notification title is required.",
                    "error"
                )
                return redirect(
                    url_for("admin.notification_create")
                )

            if not message:
                flash(
                    "Notification message is required.",
                    "error"
                )
                return redirect(
                    url_for("admin.notification_create")
                )

            if notification_type not in allowed_types:
                flash(
                    "Invalid notification type.",
                    "error"
                )
                return redirect(
                    url_for("admin.notification_create")
                )

            if is_published:
                cursor.execute("""
                    INSERT INTO notifications
                    (
                        game_id,
                        title,
                        message,
                        notification_type,
                        is_published,
                        published_at,
                        expires_at,
                        created_by
                    )
                    VALUES
                    (
                        %s, %s, %s, %s,
                        1, NOW(), %s, %s
                    )
                """, (
                    game_id,
                    title,
                    message,
                    notification_type,
                    expires_at,
                    session.get("admin_id")
                ))
            else:
                cursor.execute("""
                    INSERT INTO notifications
                    (
                        game_id,
                        title,
                        message,
                        notification_type,
                        is_published,
                        published_at,
                        expires_at,
                        created_by
                    )
                    VALUES
                    (
                        %s, %s, %s, %s,
                        0, NULL, %s, %s
                    )
                """, (
                    game_id,
                    title,
                    message,
                    notification_type,
                    expires_at,
                    session.get("admin_id")
                ))

            connection.commit()

            flash(
                "Notification created successfully.",
                "success"
            )

            return redirect(
                url_for("admin.notifications")
            )

        cursor.execute("""
            SELECT id, game_name
            FROM games
            ORDER BY game_name ASC
        """)

        games = cursor.fetchall()

        return render_template(
            "admin/notifications.html",
            notifications=[],
            games=games,
            search="",
            notification_type="all",
            create_mode=True
        )

    except Exception:
        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Notification creation error"
        )

        flash(
            "Unable to create notification.",
            "error"
        )

        return redirect(
            url_for("admin.notifications")
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# TOGGLE NOTIFICATION
# ============================================================

@admin_bp.route(
    "/notifications/<int:notification_id>/toggle",
    methods=["POST"]
)
@admin_required
def notification_toggle(notification_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                title,
                is_published
            FROM notifications
            WHERE id = %s
            LIMIT 1
        """, (notification_id,))

        notification = cursor.fetchone()

        if not notification:
            flash(
                "Notification not found.",
                "error"
            )
            return redirect(
                url_for("admin.notifications")
            )

        if notification["is_published"]:
            cursor.execute("""
                UPDATE notifications
                SET
                    is_published = 0,
                    published_at = NULL
                WHERE id = %s
            """, (notification_id,))

            message = "Notification unpublished."
        else:
            cursor.execute("""
                UPDATE notifications
                SET
                    is_published = 1,
                    published_at = NOW(),
                    created_by = COALESCE(
                        created_by,
                        %s
                    )
                WHERE id = %s
            """, (
                session.get("admin_id"),
                notification_id
            ))

            message = "Notification published."

        connection.commit()

        flash(
            message,
            "success"
        )

    except Exception:
        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Notification toggle error"
        )

        flash(
            "Unable to change notification status.",
            "error"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("admin.notifications")
    )


# ============================================================
# DELETE NOTIFICATION
# ============================================================

@admin_bp.route(
    "/notifications/<int:notification_id>/delete",
    methods=["POST"]
)
@admin_required
def notification_delete(notification_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id
            FROM notifications
            WHERE id = %s
            LIMIT 1
        """, (notification_id,))

        if not cursor.fetchone():
            flash(
                "Notification not found.",
                "error"
            )
            return redirect(
                url_for("admin.notifications")
            )

        cursor.execute("""
            DELETE FROM notifications
            WHERE id = %s
        """, (notification_id,))

        connection.commit()

        flash(
            "Notification deleted successfully.",
            "success"
        )

    except Exception:
        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Notification deletion error"
        )

        flash(
            "Unable to delete notification.",
            "error"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("admin.notifications")
    )



# ============================================================
# ADMIN SETTINGS
# ============================================================

@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # CREATE SETTINGS TABLE IF IT DOES NOT EXIST
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portal_settings (
                id INT PRIMARY KEY,
                portal_name VARCHAR(150) NOT NULL,
                event_date DATE NULL,
                portal_status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
                registration_enabled TINYINT(1) NOT NULL DEFAULT 1,
                student_login_enabled TINYINT(1) NOT NULL DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # CREATE DEFAULT SETTINGS RECORD
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO portal_settings
            (
                id,
                portal_name,
                event_date,
                portal_status,
                registration_enabled,
                student_login_enabled
            )
            SELECT
                1,
                'Engineers Day 2026',
                '2026-09-15',
                'ACTIVE',
                1,
                1
            WHERE NOT EXISTS (
                SELECT 1
                FROM portal_settings
                WHERE id = 1
            )
        """)

        connection.commit()

        # ----------------------------------------------------
        # SAVE SETTINGS
        # ----------------------------------------------------

        if request.method == "POST":

            portal_name = request.form.get(
                "portal_name",
                ""
            ).strip()

            event_date = request.form.get(
                "event_date",
                ""
            ).strip() or None

            portal_status = request.form.get(
                "portal_status",
                "ACTIVE"
            ).strip().upper()

            registration_enabled = (
                1
                if request.form.get("registration_enabled")
                else 0
            )

            student_login_enabled = (
                1
                if request.form.get("student_login_enabled")
                else 0
            )

            # ------------------------------------------------
            # VALIDATION
            # ------------------------------------------------

            if not portal_name:
                flash(
                    "Portal name is required.",
                    "error"
                )

                return redirect(
                    url_for("admin.settings")
                )

            if portal_status not in (
                "ACTIVE",
                "MAINTENANCE"
            ):
                flash(
                    "Invalid portal status.",
                    "error"
                )

                return redirect(
                    url_for("admin.settings")
                )

            # ------------------------------------------------
            # UPDATE
            # ------------------------------------------------

            cursor.execute("""
                UPDATE portal_settings
                SET
                    portal_name = %s,
                    event_date = %s,
                    portal_status = %s,
                    registration_enabled = %s,
                    student_login_enabled = %s
                WHERE id = 1
            """, (
                portal_name,
                event_date,
                portal_status,
                registration_enabled,
                student_login_enabled
            ))

            connection.commit()

            flash(
                "Portal settings updated successfully.",
                "success"
            )

            return redirect(
                url_for("admin.settings")
            )

        # ----------------------------------------------------
        # LOAD SETTINGS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                portal_name,
                event_date,
                portal_status,
                registration_enabled,
                student_login_enabled,
                updated_at
            FROM portal_settings
            WHERE id = 1
            LIMIT 1
        """)

        settings_data = cursor.fetchone()

        # ----------------------------------------------------
        # EVENT COUNT
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM games
        """)

        total_events = cursor.fetchone()["total"]

        return render_template(
            "admin/settings.html",
            settings=settings_data,
            total_events=total_events
        )

    except Exception:

        if connection:
            connection.rollback()

        current_app.logger.exception(
            "Admin settings error"
        )

        flash(
            "Unable to load settings.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
