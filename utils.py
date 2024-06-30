import re
import os
import requests
from pyairtable import Api
from geopy.geocoders import Nominatim

GOOGLE_API_LOGO = os.getenv("GOOGLE_API_LOGO")
GOOGLE_SEARCHENGINE_KEY = os.getenv("GOOGLE_SEARCHENGINE_KEY")

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")

api = Api(AIRTABLE_TOKEN)
table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)


SKILLS_TO_SEARCH = [
    "Devops",
    "Machine Learning",
    "Data Science",
    "Data Scientist",
    # "Data Analytics",
    "Business Intelligence",
    "Bayesian",
    # "Data Engineering",
    "Data Engineer",
    "MLOps",
    "ETL",
    "DBT",
    "Sports Analytics",
    "Data Visualization",
    "A/B testing",
    "Tableau",
    "Power BI",
]


def get_recent_urls():
    # URLS POSTED IN THE LAST MONTH
    all = table.all(formula="{days_since_uploaded} < 30")
    recent_urls = [record["fields"]["url"] for record in all]
    return recent_urls


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


def add_sport_list(title, description):
    # Sport
    sport_list = []
    if re.search(
        r"\b(?:basketball|nba)\b",
        description,
        re.IGNORECASE,
    ):
        sport_list += ["Basketball"]
    elif re.search(r"\b(?:football|NFL)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["Football"]
    elif re.search(
        r"\b(?:football|soccer|MLS)\b", title + " " + description, re.IGNORECASE
    ):
        sport_list += ["Football"]
    elif re.search(r"\b(?:baseball|MLB)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["Baseball"]
    elif re.search(r"\b(?:hockey|NHL)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["Hockey"]
    elif re.search(r"\b(?:golf|PGA)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["Golf"]
    elif re.search(r"\b(?:tennis|ATP)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["Tennis"]
    elif re.search(r"\b(?:rugby|NRL)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["Rugby"]
    elif re.search(r"\b(?:mma|ufc)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["MMA"]
    elif re.search(r"\b(?:boxing)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["Boxing"]

    return sport_list


def add_industry(title, description):
    # Industry
    industry = []
    if re.search(
        r"\b(?:sports betting|betting|gambling)\b",
        title + " " + description,
        re.IGNORECASE,
    ):
        industry += ["Betting"]
    elif re.search(r"\b(?:esports|esport)\b", title + " " + description, re.IGNORECASE):
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


def get_skills_required(description, skills_to_search=SKILLS_TO_SEARCH):

    skills_column = [field for field in table.schema().fields if field.name == "skills"]
    skills = [skill.name for skill in skills_column[0].options.choices]

    skills = skills + skills_to_search
    skills = sorted(skills, key=len, reverse=True)

    # These are the main skills we want to filter by
    pattern = r"\b(?:" + "|".join(skills_to_search) + r")\b"
    skills_required = [
        skill.lower() for skill in set(re.findall(pattern, description, re.IGNORECASE))
    ]
    skills_required_format = [
        skill for skill in set(skills) if skill.lower() in skills_required
    ]

    # These are all the skills including some generic ones such as Data, Analytics, etc that could appear in other jobs that we don't want to keep only because they have those.
    escaped_skills = [re.escape(skill) for skill in skills]
    pattern = r"\b(?:" + "|".join(escaped_skills) + r")\b"
    all_skills = [
        skill.lower() for skill in set(re.findall(pattern, description, re.IGNORECASE))
    ]
    all_skills_format = [skill for skill in skills if skill.lower() in all_skills]

    return skills_required_format, all_skills_format


def clean_location(location):
    location = location.lower()
    location = location.split("/")[0]
    location = location.split("-")[0]
    location = location.split("or")[0]
    location = location.replace("remote", "")
    location = location.replace("hybrid", "")
    location = location.replace("in office", "")
    return location


def find_country(location_str):
    try:
        location_str = clean_location(location_str)
        geolocator = Nominatim(user_agent="sportsjobs")
        location = geolocator.geocode(
            location_str, exactly_one=True, addressdetails=True, language="en"
        )

        if location:
            # Access the address dictionary
            address = location.raw.get("address", {})
            # Get the country
            country = address.get("country", "Country not found")
            return country.lower()
        else:
            return "united states"
    except Exception as e:
        print(f"Error finding country: {e}")
        return "united states"


def get_remote_status(full_description, location, title):
    if (
        ("remote" in location.lower())
        | ("remote" in title.lower())
        | ("remote" in full_description.lower())
    ):
        accepts_remote = "Yes"
    else:
        accepts_remote = "No"
    return accepts_remote


def get_seniority_level(title):
    if re.search(
        r"\b(?:intern|internship|internships)\b",
        title,
        re.IGNORECASE,
    ):
        seniority = "Internship"
    elif re.search(r"\b(?:junior)\b", title, re.IGNORECASE):
        seniority = "Junior"
    else:
        seniority = "With Experience"
    return seniority


def get_hours(title, description, hours="Full-time"):
    if re.search(
        r"\b(?:part time|parttime)\b", title + " " + description, re.IGNORECASE
    ):
        hours = "Part time"

    if hours in ["Part-time", "Parttime"]:
        hours = "Part time"

    if hours != "Part time" and hours != "Fulltime":
        hours = "Fulltime"

    return hours
