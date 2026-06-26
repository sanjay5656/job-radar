import os
import requests
import json
import time

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def score_job(resume_text, job, retries=3):
    api_key = os.environ["GEMINI_API_KEY"]
    prompt = f"""You are a strict technical recruiter screening a fresher candidate.

CRITICAL FIRST CHECK: Identify the primary programming language(s)/framework(s) the JD requires.
If the JD requires a language/framework the resume does NOT mention at all, cap match_score at 30,
regardless of other buzzword overlap (REST API, Docker, CI/CD do not substitute for the core language).

Return ONLY valid JSON, no markdown, no preamble, in this exact format:
{{
  "match_score": <integer 0-100>,
  "match_summary": "<2-3 sentences explaining specifically how the resume matches or fails to match THIS job description>",
  "ats_keywords": ["array of 8-15 exact keywords/phrases from this JD an ATS would scan for"],
  "missing_keywords": ["array of must-have keywords from the JD that are NOT in the resume"]
}}

RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
Title: {job['title']}
Company: {job['company']}
{job['description'][:3000]}
"""
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(retries):
        try:
            resp = requests.post(f"{GEMINI_URL}?key={api_key}", json=body, timeout=30)
            if resp.status_code == 429:
                time.sleep(6)
                continue
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw_text)
            return parsed
        except Exception as e:
            print(f"Scoring failed (attempt {attempt+1}): {e}")
            time.sleep(2)
    return {"match_score": 0, "match_summary": "Scoring failed", "ats_keywords": [], "missing_keywords": []}