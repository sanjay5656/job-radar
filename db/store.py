import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "jobs.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            url TEXT,
            description TEXT,
            source TEXT,
            match_score INTEGER,
            match_summary TEXT,
            ats_keywords TEXT,
            missing_keywords TEXT,
            sent INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def job_exists(conn, job_id):
    cur = conn.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
    return cur.fetchone() is not None

def insert_job(conn, job):
    conn.execute("""
        INSERT OR IGNORE INTO jobs (job_id, title, company, location, url, description, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (job["job_id"], job["title"], job["company"], job["location"],
          job["url"], job["description"], job["source"]))
    conn.commit()

def update_score(conn, job_id, result):
    import json
    conn.execute("""
        UPDATE jobs SET match_score = ?, match_summary = ?, ats_keywords = ?, missing_keywords = ?
        WHERE job_id = ?
    """, (
        result["match_score"], result["match_summary"],
        json.dumps(result.get("ats_keywords", [])),
        json.dumps(result.get("missing_keywords", [])),
        job_id
    ))
    conn.commit()

def get_unsent_scored_jobs(conn, threshold, limit):
    cur = conn.execute("""
        SELECT job_id, title, company, location, url, match_score, match_summary, ats_keywords, missing_keywords
        FROM jobs
        WHERE sent = 0 AND match_score >= ?
        ORDER BY match_score DESC
        LIMIT ?
    """, (threshold, limit))
    return cur.fetchall()

def mark_sent(conn, job_ids):
    conn.executemany("UPDATE jobs SET sent = 1 WHERE job_id = ?", [(j,) for j in job_ids])
    conn.commit()