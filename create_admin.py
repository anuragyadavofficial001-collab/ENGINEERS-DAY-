import getpass
import pymysql
from werkzeug.security import generate_password_hash

from config import Config


def main():

    print()
    print("========================================")
    print("      ENGINEERS DAY - CREATE ADMIN")
    print("========================================")
    print()

    username = input("Enter Admin Username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    full_name = input("Enter Admin Full Name: ").strip()

    if not full_name:
        print("Name cannot be empty.")
        return

    password = getpass.getpass("Enter Admin Password: ")

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    confirm_password = getpass.getpass(
        "Confirm Admin Password: "
    )

    if password != confirm_password:
        print("Passwords do not match.")
        return

    password_hash = generate_password_hash(
        password,
        method="scrypt"
    )

    connection = None
    cursor = None

    try:

        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            port=Config.MYSQL_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM admins
            WHERE username = %s
            LIMIT 1
            """,
            (username,)
        )

        existing = cursor.fetchone()

        if existing:

            print()
            print("Admin username already exists.")
            return

        cursor.execute(
            """
            INSERT INTO admins
            (
                username,
                password_hash,
                full_name,
                is_active
            )
            VALUES
            (
                %s,
                %s,
                %s,
                TRUE
            )
            """,
            (
                username,
                password_hash,
                full_name
            )
        )

        connection.commit()

        print()
        print("========================================")
        print("ADMIN CREATED SUCCESSFULLY")
        print("Username:", username)
        print("Name:", full_name)
        print("========================================")
        print()

    except Exception as e:

        if connection:
            connection.rollback()

        print()
        print("ERROR:", e)
        print()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    main()