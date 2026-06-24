import re

def passes_stage1(job, config):
    text = (job["title"] + " " + job["description"]).lower()

    # exclude obviously senior/irrelevant titles
    for bad in config.get("exclude_titles", []):
        if bad.lower() in job["title"].lower():
            return False

    # must mention at least one of our target keywords
    if not any(k.lower() in text for k in config.get("must_have_any", [])):
        return False

    # location check (skip for remote jobs)
    locations = [l.lower() for l in config.get("locations", [])]
    if job["source"] != "remoteok":
        if locations and not any(loc in job["location"].lower() for loc in locations):
            return False

    # experience check via regex
    exp_min = config.get("experience_min", 0)
    exp_max = config.get("experience_max", 99)
    match = re.search(r"(\d+)\s*[-+]?\s*(?:to)?\s*(\d+)?\s*years?", text)
    if match:
        lo = int(match.group(1))
        hi = int(match.group(2)) if match.group(2) else lo
        if lo > exp_max:
            return False

    return True