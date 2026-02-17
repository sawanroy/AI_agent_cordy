import pandas as pd
from db import get_connection


def export_csv(output_path="cordyceps_full_report.csv"):
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM intelligence;", conn)
        df.to_csv(output_path, index=False)
    finally:
        conn.close()
