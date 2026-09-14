import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:

    # Flask secret key
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "engineers-day-secret-key"
    )

    # MySQL configuration
    MYSQL_HOST = os.getenv(
        "MYSQL_HOST",
        "127.0.0.1"
    )

    MYSQL_USER = os.getenv(
        "MYSQL_USER",
        "root"
    )

    MYSQL_PASSWORD = os.getenv(
        "MYSQL_PASSWORD",
        ""
    )

    MYSQL_DATABASE = os.getenv(
        "MYSQL_DATABASE",
        "engineers_day"
    )

    MYSQL_PORT = int(
        os.getenv(
            "MYSQL_PORT",
            "3306"
        )
    )