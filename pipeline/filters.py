import re

FRESHER_SIGNALS = ["fresher", "entry level", "entry-level", "no experience",
                    "0 year", "graduate", "trainee", "campus"]

def passes_stage1(job, config):
    title = job["title"].lower()
    text = (job["title"] + " " + job["description"]).lower()

    # hard exclude: clearly senior/irrelevant titles
    for bad in config.get("exclude_titles", []):
        if bad.lower() in title:
            return False

    # domain check — title OR full text, broad net on purpose
    if not any(k.lower() in text for k in config.get("domain_keywords", [])):
        return False

    # location check (skip for remote jobs)
    locations = [l.lower() for l in config.get("locations", [])]
    if job["source"] != "remoteok":
        if locations and not any(loc in job["location"].lower() for loc in locations):
            return False

    # experience check — handle digits AND words
    exp_max = config.get("experience_max", 99)

    if any(sig in text for sig in FRESHER_SIGNALS):
        return True  # explicitly fresher-friendly language, always pass

    numbers = re.findall(r"(\d+)\s*\+?\s*years?", text)
    if numbers:
        years_mentioned = [int(n) for n in numbers]
        min_years_required = min(years_mentioned)
        # only exclude if EVERY mention is clearly above our ceiling
        if min_years_required > exp_max:
            return False

    return True  # no clear experience signal at all -> let it through, Gemini will judge