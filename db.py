import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
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
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_intelligence(data):
    conn = get_connection()
    cur = conn.cursor()

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

    conn.commit()
    cur.close()
    conn.close()

def fetch_all():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM intelligence;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows
