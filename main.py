import yaml
from pathlib import Path

from db.store import get_conn, job_exists, insert_job, update_score, get_unsent_scored_jobs, mark_sent
from sources.adzuna import fetch_adzuna_jobs
from sources.remoteok import fetch_remoteok_jobs
from sources.jooble import fetch_jooble_jobs
from pipeline.filters import passes_stage1
from pipeline.scorer import score_job
from pipeline.title_generator import generate_search_terms
from delivery.emailer import send_digest
from sources.arbeitnow import fetch_arbeitnow_jobs
from sources.jobicy import fetch_jobicy_jobs

def main():
    config = yaml.safe_load(open("config.yaml"))
    resume_text = Path("resume.txt").read_text()

    conn = get_conn()

    search_terms = generate_search_terms(resume_text)

    raw_jobs = (
        fetch_adzuna_jobs(config["locations"], search_terms)
        + fetch_remoteok_jobs()
        + fetch_jooble_jobs(search_terms, location=config["locations"][0])
        + fetch_arbeitnow_jobs()
        + fetch_jobicy_jobs()
    )
    print(f"Fetched {len(raw_jobs)} raw jobs.")

    new_jobs = []
    for job in raw_jobs:
        if not job_exists(conn, job["job_id"]):
            insert_job(conn, job)
            new_jobs.append(job)

    print(f"{len(new_jobs)} new jobs after dedupe.")

    candidates = []
    for j in new_jobs:
        passed, reason = passes_stage1(j, config, resume_text)
        if passed:
            candidates.append(j)
        else:
            print(f"Filtered out: {j['title']} @ {j['company']} — {reason}")
    print(f"{len(candidates)} candidates after stage-1 filter.")

    for job in candidates:
        result = score_job(resume_text, job)
        update_score(conn, job["job_id"], result)
        print(f"Scored {job['title']} @ {job['company']}: {result['match_score']}%")

    to_send = get_unsent_scored_jobs(
        conn,
        threshold=config["match_score_threshold"],
        limit=config["top_n_in_email"]
    )

    send_digest(to_send)
    mark_sent(conn, [row[0] for row in to_send])

    conn.close()

if __name__ == "__main__":
    main()