from db.store import get_conn
import sqlite3

conn = get_conn()
columns_to_add = [
    ("match_summary", "TEXT"),
    ("ats_keywords", "TEXT"),
    ("missing_keywords", "TEXT"),
    ("posted_date", "TEXT"),
]
for col, col_type in columns_to_add:
    try:
        conn.execute(f"ALTER TABLE jobs ADD COLUMN {col} {col_type}")
        conn.commit()
        print(f"Added column: {col}")
    except sqlite3.OperationalError:
        print(f"Column already exists: {col}")
conn.close()