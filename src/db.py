"""
Database Abstraction Layer for PaperForge
Supports SQLite (in-memory/file), MySQL, and PostgreSQL via DB_TYPE environment variable.
"""
import os
import sqlite3
from typing import List, Tuple, Any

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "paperforge")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "paperforge")

def execute_sql_query(query: str) -> Tuple[List[Any], str]:
    """
    Executes a SQL query against configured DB backend.
    Returns (rows, error_message).
    """
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "mysql":
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall() if cursor.description else []
            conn.commit()
            conn.close()
            return rows, ""
        except Exception as e:
            return [], str(e)

    elif db_type == "postgres" or db_type == "postgresql":
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                dbname=POSTGRES_DATABASE
            )
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall() if cursor.description else []
            conn.commit()
            conn.close()
            return rows, ""
        except Exception as e:
            return [], str(e)

    else:
        # Default: SQLite In-Memory Engine
        try:
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE sales (id INTEGER PRIMARY KEY, amount REAL, region TEXT);")
            cursor.execute("INSERT INTO sales (amount, region) VALUES (1500.0, 'North'), (2500.0, 'South');")
            conn.commit()

            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            return rows, ""
        except Exception as e:
            return [], str(e)
