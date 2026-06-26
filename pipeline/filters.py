import re
from pipeline.skills_dictionary import ALL_SKILLS, detect_required_languages, candidate_has_language

FRESHER_SIGNALS = [
    "fresher", "freshers", "entry level", "entry-level", "no experience",
    "0 year", "0-1 year", "0 to 1", "graduate engineer", "trainee",
    "campus hire", "0+ years", "any experience"
]

BANGALORE_AREAS = [
    "bangalore", "bengaluru", "electronic city", "whitefield", "koramangala",
    "btm", "marathahalli", "indiranagar", "hsr layout", "jp nagar",
    "yelahanka", "hebbal", "bellandur", "sarjapur", "jayanagar", "rajajinagar",
    "malleshwaram", "banashankari"
]

def passes_stage1(job, config, resume_text):
    title = job["title"].lower()
    text = (job["title"] + " " + job["description"]).lower()

    # hard exclude: clearly senior/irrelevant titles
    for bad in config.get("exclude_titles", []):
        if bad.lower() in title:
            return False, "Excluded by seniority/title keyword"

    # SKILL-BASED domain check — title is ignored, only skills matter
    matched_skills = [s for s in ALL_SKILLS if s.strip() in text]
    if not matched_skills:
        return False, "No relevant skills found in JD"

    # HARD LANGUAGE GATE — the Klubworks/Enan Tech fix
    required_langs = detect_required_languages(text)
    if required_langs:
        has_match = any(candidate_has_language(resume_text, lang) for lang in required_langs)
        if not has_match:
            return False, f"JD requires {required_langs}, not in resume"

    # location — must be somewhere in Bangalore (broad area match), skip for remote
    if job["source"] != "remoteok":
        if not any(area in job["location"].lower() for area in BANGALORE_AREAS):
            return False, "Not in Bangalore area"

    # experience — fresher-aware
    exp_max = config.get("experience_max", 3)
    if any(sig in text for sig in FRESHER_SIGNALS):
        return True, "Fresher-friendly language detected"

    numbers = re.findall(r"(\d+)\s*\+?\s*years?", text)
    if numbers:
        min_years_required = min(int(n) for n in numbers)
        if min_years_required > exp_max:
            return False, f"Requires {min_years_required}+ years, above threshold"
        return True, "Experience range acceptable"

    # no experience info mentioned at all -> let it through, don't penalize ambiguity
    return True, "No experience requirement stated, included by default"