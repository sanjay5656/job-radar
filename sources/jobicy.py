import requests

def fetch_jobicy_jobs():
    jobs = []
    try:
        resp = requests.get("https://jobicy.com/api/v2/remote-jobs?count=30&tag=python", timeout=20)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("jobs", []):
            jobs.append({
                "job_id": "jobicy_" + str(item.get("id")),
                "title": item.get("jobTitle", ""),
                "company": item.get("companyName", "Unknown"),
                "location": item.get("jobGeo", "Remote"),
                "url": item.get("url", ""),
                "description": item.get("jobExcerpt", "")[:3000],
                "source": "jobicy",
                "posted_date": item.get("created", ""),
            })
    except Exception as e:
        print(f"Jobicy fetch failed: {e}")
    return jobs