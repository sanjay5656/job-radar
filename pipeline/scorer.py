import os
import requests
import json
import time

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def score_job(resume_text, job, retries=3):
    api_key = os.environ["GEMINI_API_KEY"]
    prompt = f"""You are a strict technical recruiter screening a fresher candidate.

Step 1: List the 3-5 hard MUST-HAVE requirements in this JD (skills, degree, experience floor).
Step 2: For each, check if the resume actually demonstrates it — yes/no/partial.
Step 3: Based on that checklist (not vibes), compute a realistic match_score 0-100.
A candidate missing 2+ must-haves should score below 40, even if other skills overlap.

Return ONLY valid JSON, no markdown, no preamble:
{{"match_score": <integer 0-100>, "reason": "<one sentence citing the key match or gap>"}}

RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
Title: {job['title']}
Company: {job['company']}
{job['description'][:3000]}
"""
    # rest of function unchanged
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(retries):
        try:
            resp = requests.post(
                f"{GEMINI_URL}?key={api_key}",
                json=body,
                timeout=30
            )
            if resp.status_code == 429:
                time.sleep(6)
                continue
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw_text)
            return parsed.get("match_score", 0), parsed.get("reason", "")
        except Exception as e:
            print(f"Scoring failed (attempt {attempt+1}): {e}")
            time.sleep(2)
    return 0, "Scoring failed"