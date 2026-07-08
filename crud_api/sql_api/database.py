"""MySQL connection for the `energy_db` schema defined in
`Database design/sql/schema.sql`. Override via env vars if needed.
"""
import os

import mysql.connector

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "energy_db"),
}


def get_db():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        yield conn
    finally:
        conn.close()
