import os
import requests

def fetch_adzuna_jobs(locations, max_results=50):
    app_id = os.environ["ADZUNA_APP_ID"]
    app_key = os.environ["ADZUNA_APP_KEY"]
    jobs = []
    for loc in locations:
        url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "what": "python developer OR machine learning OR backend developer",
            "where": loc,
            "results_per_page": max_results,
            "content-type": "application/json",
        }
        try:
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("results", []):
                jobs.append({
                    "job_id": "adzuna_" + str(item.get("id")),
                    "title": item.get("title", ""),
                    "company": item.get("company", {}).get("display_name", "Unknown"),
                    "location": item.get("location", {}).get("display_name", loc),
                    "url": item.get("redirect_url", ""),
                    "description": item.get("description", ""),
                    "source": "adzuna",
                })
        except Exception as e:
            print(f"Adzuna fetch failed for {loc}: {e}")
    return jobs