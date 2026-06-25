import os
import requests

def fetch_jooble_jobs(search_terms, location="Bangalore", max_results=20):
    api_key = os.environ.get("JOOBLE_API_KEY")
    if not api_key:
        print("JOOBLE_API_KEY not set, skipping Jooble.")
        return []

    url = f"https://jooble.org/api/{api_key}"
    jobs = []
    seen_ids = set()
    for term in search_terms[:8]:
        body = {"keywords": term, "location": location}
        try:
            resp = requests.post(url, json=body, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            print(f"Jooble '{term}': {len(data.get('jobs', []))} returned")
            for item in data.get("jobs", []):
                job_id = "jooble_" + str(hash(item.get("link", "")))
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)
                jobs.append({
                    "job_id": job_id,
                    "title": item.get("title", ""),
                    "company": item.get("company", "Unknown"),
                    "location": item.get("location", location),
                    "url": item.get("link", ""),
                    "description": item.get("snippet", ""),
                    "source": "jooble",
                })
        except Exception as e:
            print(f"Jooble fetch failed for '{term}': {e}")
    return jobs