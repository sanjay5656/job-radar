import requests

def fetch_arbeitnow_jobs():
    jobs = []
    try:
        resp = requests.get("https://www.arbeitnow.com/api/job-board-api", timeout=20)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("data", []):
            location = item.get("location", "") or ""
            if "india" not in location.lower() and "bangalore" not in location.lower() and not item.get("remote", False):
                continue
            jobs.append({
                "job_id": "arbeitnow_" + str(item.get("slug")),
                "title": item.get("title", ""),
                "company": item.get("company_name", "Unknown"),
                "location": location or "Remote",
                "url": item.get("url", ""),
                "description": item.get("description", "")[:3000],
                "source": "arbeitnow",
            })
    except Exception as e:
        print(f"Arbeitnow fetch failed: {e}")
    return jobs