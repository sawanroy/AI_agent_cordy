import logging
import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )


def init_db():
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
        CREATE TABLE IF NOT EXISTS intelligence (
            id SERIAL PRIMARY KEY,
            source_type TEXT,
            title TEXT,
            entity TEXT,
            year TEXT,
            country TEXT,
            summary TEXT,
            price TEXT,
            moq TEXT,
            certifications TEXT,
            contact_email TEXT,
            phone TEXT,
            url TEXT,
            doi_or_patent TEXT
        );
    """
                )
    except Exception:
        logging.exception("Database initialization failed")
        raise
    finally:
        if conn:
            conn.close()


def insert_intelligence(data):
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
        INSERT INTO intelligence (
            source_type, title, entity, year, country,
            summary, price, moq, certifications,
            contact_email, phone, url, doi_or_patent
        ) VALUES (%s, %s, %s, %s, %s,
                  %s, %s, %s, %s,
                  %s, %s, %s, %s)
    """,
                    (
                        data.get("source_type"),
                        data.get("title"),
                        data.get("entity"),
                        data.get("year"),
                        data.get("country"),
                        data.get("summary"),
                        data.get("price"),
                        data.get("moq"),
                        data.get("certifications"),
                        data.get("contact_email"),
                        data.get("phone"),
                        data.get("url"),
                        data.get("doi_or_patent"),
                    ),
                )
    except Exception:
        logging.exception("Failed to insert intelligence record")
        raise
    finally:
        if conn:
            conn.close()


def fetch_all():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM intelligence;")
            rows = cur.fetchall()
        return rows
    except Exception:
        logging.exception("Failed to fetch intelligence records")
        raise
    finally:
        if conn:
            conn.close()
