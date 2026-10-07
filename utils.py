import re
import os
import requests
from pyairtable import Api
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

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
    "Software Engineer",
    "Software Engineering",
    "Data Analytics",
    "Business Intelligence",
    "Bayesian",
    "Data Engineering",
    "Data Engineer",
    "MLOps",
    "ETL",
    "DBT",
    "Sports Analytics",
    "Data Visualization",
    "A/B testing",
    "Tableau",
    "Power BI",
    "Engineer",
    "Analytics",
    "AI",
    "Researcher",
    "research",
    "STEM",
    "NFL",
    "NBA",
    "MLB",
    "NHL",
    "Soccer",
    "Football",
    "Baseball",
    "Hockey",
    "Basketball",
    "Golf",
    "Tennis",
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
        title + " " + description,
        re.IGNORECASE,
    ):
        sport_list += ["Basketball"]
    elif re.search(r"\b(?:football|NFL)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["Football - NFL"]
    elif re.search(
        r"\b(?:football|soccer|MLS)\b", title + " " + description, re.IGNORECASE
    ):
        sport_list += ["Football - Soccer"]
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
    elif re.search(r"\b(?:formula1)\b", title + " " + description, re.IGNORECASE):
        sport_list += ["Formula 1"]

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


# Separators between alternative locations ("London / Remote", "NYC or Boston", "Austin - Hybrid").
# They must be whole separators: splitting on bare substrings turned "Baltimore" into "baltim" (Egypt)
# and "Atlanta, Georgia" into "atlanta, ge" (Indonesia). "or" right after a comma is Oregon ("Portland, OR").
# "·" is not one of them: "St. Petersburg · FL" is city and state, so it is read as a comma.
LOCATION_ALTERNATIVES = re.compile(r"\s*(?:/|\||;|\s-\s|(?<!,)\s+or\s+)\s*", re.IGNORECASE)
LOCATION_NOISE = re.compile(
    r"\b(?:fully remote|remote|hybrid|in[- ]office|on[- ]site|onsite)\b", re.IGNORECASE
)

DEFAULT_COUNTRY = {"country": "united states", "country_code": "US"}

# Locations that already state the country. Checked before geocoding, which misreads some
# of them (Nominatim returns New Zealand for "Vancouver, BC V6B0N8, CAN").
EXPLICIT_COUNTRIES = {
    "us": DEFAULT_COUNTRY,
    "usa": DEFAULT_COUNTRY,
    "united states": DEFAULT_COUNTRY,
    "united states of america": DEFAULT_COUNTRY,
    "uk": {"country": "united kingdom", "country_code": "GB"},
    "united kingdom": {"country": "united kingdom", "country_code": "GB"},
    "england": {"country": "united kingdom", "country_code": "GB"},
    "scotland": {"country": "united kingdom", "country_code": "GB"},
    "wales": {"country": "united kingdom", "country_code": "GB"},
    "northern ireland": {"country": "united kingdom", "country_code": "GB"},
    "can": {"country": "canada", "country_code": "CA"},
    "canada": {"country": "canada", "country_code": "CA"},
}
# US state codes that are not also country codes seen in job locations: "Berlin, DE",
# "Bangalore, IN", "Toronto, CA", "Tel Aviv, IL" etc. are left to the geocoder.
US_STATE_CODES = {
    "ak", "az", "ct", "dc", "fl", "ga", "hi", "ia", "ks", "ky", "la", "me", "md", "mi", "mn",
    "ms", "mo", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri",
    "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy",
}
# None of these collide with US state codes.
CANADIAN_PROVINCE_CODES = {"ab", "bc", "mb", "nb", "nl", "ns", "nt", "nu", "on", "pe", "qc", "sk", "yt"}

# Nominatim allows at most one request per second; the old code made two unthrottled
# calls per job with a 1s timeout, and every failure silently became "united states".
_geolocator = Nominatim(user_agent="sportsjobs", timeout=10)
_geocode = RateLimiter(
    _geolocator.geocode, min_delay_seconds=1, max_retries=2, error_wait_seconds=5, swallow_exceptions=False
)
_country_cache = {}


def clean_location(location):
    """Lowercase the first real alternative in a location string, without remote/hybrid noise."""
    for part in LOCATION_ALTERNATIVES.split(location.lower().replace("·", ",")):
        part = LOCATION_NOISE.sub("", part)
        part = re.sub(r"\s*,[\s,]*", ", ", part)  # "nj , , hybrid" -> "nj, hybrid"
        part = re.sub(r"\s{2,}", " ", part).strip(" ,()-")
        if part:
            return part
    return ""


def _explicit_country(cleaned_location):
    """Country stated in the text itself: a trailing country name, or a state/province code after a comma."""
    # "UK based, with travel" -> "uk"
    tokens = [re.sub(r"\s+based$", "", token.strip()) for token in cleaned_location.split(",") if token.strip()]
    for token in reversed(tokens):
        if token in EXPLICIT_COUNTRIES:
            return EXPLICIT_COUNTRIES[token]
    for token in tokens[1:]:
        first_word = token.split()[0]
        if first_word in US_STATE_CODES:
            return DEFAULT_COUNTRY
        if first_word in CANADIAN_PROVINCE_CODES:
            return EXPLICIT_COUNTRIES["canada"]
    return None


def _geocode_country(query, **kwargs):
    """Cached, rate-limited Nominatim lookup returning {"country", "country_code"} or None."""
    cache_key = repr((query, sorted(kwargs.items())))
    if cache_key in _country_cache:
        return _country_cache[cache_key]
    try:
        location = _geocode(query, exactly_one=True, addressdetails=True, language="en", **kwargs)
    except Exception as e:
        print(f"Error finding country for {query!r}: {e}")
        return None  # not cached, so a transient failure can succeed later in the run
    address = location.raw.get("address", {}) if location else {}
    result = None
    if address.get("country") and address.get("country_code"):
        result = {"country": address["country"].lower(), "country_code": address["country_code"].upper()}
    _country_cache[cache_key] = result
    return result


def find_country(location_str):
    """Always returns {"country", "country_code"}; falls back to the US, and logs when it does."""
    cleaned = clean_location(location_str or "")
    result = None
    if cleaned:
        result = _explicit_country(cleaned) or _geocode_country(cleaned)
    if not result:
        print(f"Country not found for location {location_str!r}; defaulting to united states")
        return dict(DEFAULT_COUNTRY)
    return dict(result)


def country_from_code(country_code):
    """English country name for an ISO alpha-2 code, matching the names find_country stores."""
    code = (country_code or "").strip().lower()
    if not code:
        return None
    if code in ("us", "gb"):
        return "united states" if code == "us" else "united kingdom"
    result = _geocode_country({"country": code}, country_codes=[code], featuretype="country")
    return result["country"] if result else None


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


# def extract_salary(full_description):
#     # Define regex patterns to match salary formats
#     salary_patterns = [
#         r"\$\d+(?:,\d{3})*(?:\.\d+)?",  # matches $ followed by numbers with optional commas and decimal point
#         r"\d+(?:,\d{3})*(?:\.\d+)?\s?USD",  # matches numbers followed by USD with optional commas and decimal point
#         r"\d+(?:,\d{3})*(?:\.\d+)?\s?(?:dollars|Dollars)",  # matches numbers followed by 'dollars' or 'Dollars'
#         r"\d+\s?-\s?\d+(?:,\d{3})*(?:\.\d+)?\s?USD",  # matches salary ranges like "50,000 - 60,000 USD"
#         r"\d+\s?-\s?\d+(?:,\d{3})*(?:\.\d+)?\s?(?:dollars|Dollars)",  # matches salary ranges like "50,000 - 60,000 dollars"
#     ]

#     # Combine all patterns into a single pattern
#     combined_pattern = "|".join(salary_patterns)

#     # Search for the pattern in the text
#     matches = re.findall(combined_pattern, full_description)

#     return matches

### Old one that was in prod
# def extract_salary(text):
#     # Define regex patterns to match salary formats including ranges and prefixes
#     salary_patterns = [
#         r"\$\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:k)?\s?[-to]\s?\$\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:k)?(?:\s?(?:USD|Dollars|dollars)?)?",  # matches "$40,000-$60,000", "$40k-$100k USD"
#         r"\d{1,3}(?:,\d{3})*(?:k)?\s?[-to]\s?\d{1,3}(?:,\d{3})*(?:k)?(?:\s?\$)?(?:\s?(?:USD|Dollars|dollars)?)?",  # matches "40k-100k USD", "100,000-190,000", "125k-$145k USD"
#         # r'\$\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:k)?', # matches single amounts like "$40,000", "$40k"
#         r"\d{1,3}(?:,\d{3})*(?:k)?(?:\s?(?:USD|Dollars|dollars|K|k))",  # matches single amounts like "40k USD", "100,000 Dollars"
#         r"\$\d+\.\d{2}\s?(?:USD|usd|Usd)?/?\s?(?:hour|hr)",  # matches hourly rates like "$17.50 USD/hour"
#         r"\$?\d{1,3}(?:,\d{3})*(?:k)?\s?[-to]\s?\$\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:k)?",  # matches "$110-145,000"
#     ]

#     # Combine all patterns into a single pattern
#     combined_pattern = "|".join(salary_patterns)

#     # Search for the pattern in the text
#     matches = re.findall(combined_pattern, text, re.IGNORECASE)

#     # Clean the matches to remove any prefixes
#     cleaned_matches = []
#     for match in matches:
#         # Remove any prefixes and whitespace around the match
#         cleaned_match = re.sub(
#             r"^(?:pay range|base pay|salary|compensation|earnings|base salary)[:\s]*",
#             "",
#             match,
#             flags=re.IGNORECASE,
#         ).strip()
#         cleaned_matches.append(cleaned_match)

#     # Return the cleaned matches
#     return cleaned_matches


def extract_salary(text):
    # Remove benefit statements and percentages
    text = re.sub(r"\b\d+%.*?[\.,]", "", text)
    text = re.sub(r"pay \d+%", "", text)
    text = re.sub(r"\(.*?\)", "", text)

    # Currency and amount patterns
    amount_pattern = r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:k|K|m|M)?"
    currency_pattern = r"(?:€|£|\$|EUR|GBP|USD)"

    # Combined patterns without text descriptions
    patterns = [
        rf"{currency_pattern}\s*{amount_pattern}(?!\s*%)",  # $50,000
        rf"{amount_pattern}\s*{currency_pattern}(?!\s*%)",  # 50,000 EUR
    ]

    matches = []
    for pattern in patterns:
        found = re.finditer(pattern, text, re.IGNORECASE)
        for match in found:
            salary = match.group(0)
            # Clean and validate
            if any(x in salary.lower() for x in ["kaizen", "401"]):
                continue

            # Extract numeric value
            amount = float(re.sub(r"[^\d.]", "", salary))
            if any(x in salary.upper() for x in ["K"]):
                amount *= 1000
            elif any(x in salary.upper() for x in ["M"]):
                amount *= 1000000

            if 1000 <= amount <= 1000000:
                matches.append(salary.strip())

    return matches
