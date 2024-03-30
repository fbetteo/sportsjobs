import re
import os
import requests

GOOGLE_API_LOGO = os.getenv("GOOGLE_API_LOGO")
GOOGLE_SEARCHENGINE_KEY = os.getenv("GOOGLE_SEARCHENGINE_KEY")


def is_remote_global(full_description):
    # Define patterns for global remote work
    global_patterns = [
        r"\bwork from anywhere\b",
        r"\bremote worldwide\b",
        r"\bglobally remote\b",
        r"\bremote anywhere\b",
        r"\bfully remote\b",
        r"\bglobal remote\b",
    ]
    # Combine patterns into a single regex
    global_regex = re.compile("|".join(global_patterns), re.IGNORECASE)

    # Define patterns for location-specific remote work
    location_specific_patterns = [
        r"\bremote in [A-Za-z]+",  # e.g., "remote  US"
        r"\bremote\b",
        r"\bwork from home\b",
        r"\bwork remotely\b",
        r"\bremotely\b",
    ]
    location_specific_regex = re.compile(
        "|".join(location_specific_patterns), re.IGNORECASE
    )

    hybrid = re.compile(r"\bhybrid\b", re.IGNORECASE)

    # Search for global remote indicators
    global_matches = re.search(global_regex, full_description)

    # Search for location-specific remote indicators
    location_specific_matches = re.search(location_specific_regex, full_description)

    hybrid_matches = re.search(hybrid, full_description)

    # Determine if the job is for a remote position and if it's global or location-specific
    if global_matches:
        return "Global Remote"
    elif location_specific_matches and not hybrid_matches:
        return "Remote"
    else:
        return "Office"


# # Example usage
# full_description = "This is a remote UK. Must bein USA"
# print(is_remote_global(full_description))


def add_sport_list(description):
    # Sport
    sport_list = []
    if re.search(
        r"\b(?:basketball|nba)\b",
        description,
        re.IGNORECASE,
    ):
        sport_list += ["Basketball"]
    elif re.search(r"\b(?:football|NFL)\b", description, re.IGNORECASE):
        sport_list += ["Football"]
    elif re.search(r"\b(?:football|soccer|MLS)\b", description, re.IGNORECASE):
        sport_list += ["Football"]
    elif re.search(r"\b(?:baseball|MLB)\b", description, re.IGNORECASE):
        sport_list += ["Baseball"]
    elif re.search(r"\b(?:hockey|NHL)\b", description, re.IGNORECASE):
        sport_list += ["Hockey"]
    elif re.search(r"\b(?:golf|PGA)\b", description, re.IGNORECASE):
        sport_list += ["Golf"]
    elif re.search(r"\b(?:tennis|ATP)\b", description, re.IGNORECASE):
        sport_list += ["Tennis"]
    elif re.search(r"\b(?:rugby|NRL)\b", description, re.IGNORECASE):
        sport_list += ["Rugby"]
    elif re.search(r"\b(?:mma|ufc)\b", description, re.IGNORECASE):
        sport_list += ["MMA"]
    elif re.search(r"\b(?:boxing)\b", description, re.IGNORECASE):
        sport_list += ["Boxing"]

    return sport_list


def add_industry(description):
    # Industry
    industry = []
    if re.search(
        r"\b(?:sports betting|betting|gambling)\b",
        description,
        re.IGNORECASE,
    ):
        industry += ["Betting"]
    elif re.search(r"\b(?:esports|esport)\b", description, re.IGNORECASE):
        industry += ["Esports"]
    else:
        industry += ["Sports"]
    return industry


def add_job_area(skills):
    skills = " ".join(skills)  # Convert list to string
    if re.search(r"\b(?:Data Engineer|Data Engineering|ETL)\b", skills):
        return "Data Engineer"
    elif re.search(r"\b(?:Data Science|Data Scientist|Machine Learning)\b", skills):
        return "DS/ML/AI"
    else:
        return "Analytics"


def search_for_png_image(search_term):
    api_key = GOOGLE_API_LOGO
    cse_id = GOOGLE_SEARCHENGINE_KEY
    search_type = "image"
    file_type = "png"
    search_query = f"{search_term} + company logo"

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": search_query,
        "searchType": search_type,
        "fileType": file_type,
        "num": 1,  # Number of results to return. Adjust as needed.
    }

    response = requests.get(url, params=params)
    result = response.json()
    images = result.get("items", [])

    if not images:
        print("No images found.")
        return None

    # Assuming you want the first result
    first_image_url = images[0]["link"]
    # print("Found image URL:", first_image_url)
    return [{"url": first_image_url, "filename": f"{search_term}.png"}]
