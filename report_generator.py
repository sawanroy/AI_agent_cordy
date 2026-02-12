import pandas as pd
from db import get_connection


def export_csv():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM intelligence;", conn)
    df.to_csv("cordyceps_full_report.csv", index=False)
    conn.close()
