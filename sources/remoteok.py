import requests

def fetch_remoteok_jobs(keywords=("python", "machine learning", "backend")):
    jobs = []
    try:
        resp = requests.get("https://remoteok.com/api",
                             headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        for item in data:
            if not isinstance(item, dict) or "id" not in item:
                continue  # first item is a legal notice, skip
            text = (item.get("position", "") + " " + item.get("description", "")).lower()
            if any(k in text for k in keywords):
                jobs.append({
                    "job_id": "remoteok_" + str(item.get("id")),
                    "title": item.get("position", ""),
                    "company": item.get("company", "Unknown"),
                    "location": item.get("location", "Remote"),
                    "url": item.get("url", ""),
                    "description": item.get("description", "")[:3000],
                    "source": "remoteok",
                    "posted_date": item.get("created", ""),
                })
    except Exception as e:
        print(f"RemoteOK fetch failed: {e}")
    return jobs