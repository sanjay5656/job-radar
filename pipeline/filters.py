import re
from datetime import datetime, timezone, timedelta
from dateutil import parser as date_parser
from pipeline.skills_dictionary import (
    ALL_SKILLS, detect_required_languages, candidate_has_language,
    is_non_software_domain
)

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


def extract_min_years(text):
    """Returns the minimum years of experience mentioned, or None if not found."""
    patterns = [
        r"(\d+)\s*[-–to]+\s*\d+\s*years?",      # "2-5 years", "2 to 5 years"
        r"(\d+)\s*\+\s*years?",                  # "6+ years"
        r"minimum\s*(\d+)[\s-]*year",            # "minimum 1-year"
        r"(\d+)\s*years?\s*of\s*experience",     # "2 years of experience"
        r"(\d+)\s*years?",                       # generic fallback
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None


def is_too_old(posted_date_str, max_age_days):
    if not posted_date_str:
        return False
    try:
        posted_date = date_parser.parse(posted_date_str)
        if posted_date.tzinfo is None:
            posted_date = posted_date.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - posted_date
        return age > timedelta(days=max_age_days)
    except Exception:
        return False


def resume_skill_overlap(resume_text, jd_text):
    resume_lower = resume_text.lower()
    jd_skills_found = [s for s in ALL_SKILLS if s.strip() in jd_text]
    if not jd_skills_found:
        return 0.0, []
    overlap = [s for s in jd_skills_found if s in resume_lower]
    ratio = len(overlap) / len(jd_skills_found)
    return ratio, overlap


def passes_stage1(job, config, resume_text):
    title = job["title"].lower()
    text = (job["title"] + " " + job["description"]).lower()

    # 1. hard exclude: clearly senior/irrelevant titles
    for bad in config.get("exclude_titles", []):
        if bad.lower() in title:
            return False, "Excluded by seniority/title keyword"

    # 2. hard exclude: non-software specialized domains (SAP/ABAP/etc)
    if is_non_software_domain(text):
        return False, "Non-software specialized domain (SAP/ABAP/mainframe/etc)"

    # 3. skill-based domain check — must mention at least one known skill
    matched_skills = [s for s in ALL_SKILLS if s.strip() in text]
    if not matched_skills:
        return False, "No relevant skills found in JD"

    # 4. resume-skill overlap — require real overlap, not just "JD has some skill word"
    min_overlap = config.get("min_skill_overlap", 0.25)
    overlap_ratio, matched_resume_skills = resume_skill_overlap(resume_text, text)
    if overlap_ratio < min_overlap:
        return False, f"Low resume-skill overlap ({overlap_ratio:.0%})"

    # 5. hard language gate
    required_langs = detect_required_languages(text)
    if required_langs:
        has_match = any(candidate_has_language(resume_text, lang) for lang in required_langs)
        if not has_match:
            return False, f"JD requires {required_langs}, not in resume"

    # 6. location — must be somewhere in Bangalore, skip for remote
    if job["source"] != "remoteok":
        if not any(area in job["location"].lower() for area in BANGALORE_AREAS):
            return False, "Not in Bangalore area"

    # 7. posting age
    max_age_days = config.get("max_posting_age_days", 14)
    if is_too_old(job.get("posted_date", ""), max_age_days):
        return False, f"Posting older than {max_age_days} days"

    # 8. experience — fresher-aware, multi-pattern
    exp_max = config.get("experience_max", 3)
    if any(sig in text for sig in FRESHER_SIGNALS):
        return True, "Fresher-friendly language detected"

    min_years = extract_min_years(text)
    if min_years is not None:
        if min_years > exp_max:
            return False, f"Requires {min_years}+ years, above threshold of {exp_max}"
        return True, f"Experience requirement ({min_years} years) within range"

    return True, "No experience requirement detected, included by default"