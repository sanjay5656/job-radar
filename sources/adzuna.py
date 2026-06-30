import os
import requests

def fetch_adzuna_jobs(locations, search_terms, max_results=20):
    app_id = os.environ["ADZUNA_APP_ID"]
    app_key = os.environ["ADZUNA_APP_KEY"]
    jobs = []
    seen_ids = set()

    for loc in locations:
        for term in search_terms:
            url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": app_id, "app_key": app_key, "what": term,
                "where": loc, "results_per_page": max_results,
                "content-type": "application/json",
            }
            try:
                resp = requests.get(url, params=params, timeout=20)
                resp.raise_for_status()
                data = resp.json()
                print(f"Adzuna '{term}' in {loc}: {data.get('count', 0)} total, {len(data.get('results', []))} returned")
                for item in data.get("results", []):
                    job_id = str(item.get("id"))
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    jobs.append({
                        "job_id": "adzuna_" + job_id,
                        "title": item.get("title", ""),
                        "company": item.get("company", {}).get("display_name", "Unknown"),
                        "location": item.get("location", {}).get("display_name", loc),
                        "url": item.get("redirect_url", ""),
                        "description": item.get("description", ""),
                        "source": "adzuna",
                        "posted_date": item.get("created", ""),
                    })
            except Exception as e:
                print(f"Adzuna fetch failed for '{term}' in {loc}: {e}")
    return jobs
