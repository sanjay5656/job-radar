import os
import requests
import json

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def generate_search_terms(resume_text):
    api_key = os.environ["GEMINI_API_KEY"]
    prompt = f"""Based on this resume, list realistic job title variations that Indian recruiters
might actually post for a fresher/junior candidate with this background. Include variations like
"SDE-1", "Associate Software Engineer", "Trainee", "Junior X Developer", etc. — not just the obvious titles.
Return ONLY a JSON array of strings, no markdown, no preamble.

RESUME:
{resume_text[:3000]}
"""
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        resp = requests.post(f"{GEMINI_URL}?key={api_key}", json=body, timeout=30)
        resp.raise_for_status()
        raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        raw = raw.replace("```json", "").replace("```", "").strip()
        terms = json.loads(raw)
        print(f"Generated {len(terms)} search terms: {terms}")
        return terms
    except Exception as e:
        print(f"Title generation failed, falling back to defaults: {e}")
        return [
        "Associate Software Engineer",
        "Junior Python Developer",
        "ML Engineer Fresher",
        "AI Engineer Entry Level",
        "Backend Developer Python",
        "Generative AI Developer",
        "SDE-1",
        "AI/ML Developer",
        "Python Developer Fresher",
        "Machine Learning Engineer",
        "LLM Engineer",
        "Trainee Software Engineer",
        "Junior Backend Developer",
        "Junior Data Scientist",
        "FastAPI Developer"
    ]