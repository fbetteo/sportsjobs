### Greenhouse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import html

from geopy.geocoders import Nominatim

import os
from pyairtable import Api
import requests
import requests.auth
import re
from dotenv import load_dotenv, find_dotenv

os.getcwd()

# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/redditbot/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")

api = Api(AIRTABLE_TOKEN)
table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)

from datetime import datetime

# URLS POSTED IN THE LAST MONTH
all = table.all(formula="{days_since_uploaded} < 30")
recent_urls = [record["fields"]["url"] for record in all]

# LIST OF SKILLS AVAILABLE IN AIRTABLE
skills_column = [field for field in table.schema().fields if field.name == "skills"]
skills = [skill.name for skill in skills_column[0].options.choices]

skill_to_remove = [
    "Data",
    "Media",
    "IT",
    "Sports",
    "Manager",
    "Gaming",
    "Social Media",
    "baseball",
    "kpi",
    "Networks",
    "Excel",
    "Powerpoint",
    "Analytics",
    "Statistics",
]

for skill in skill_to_remove:
    skills.remove(skill)

skills_to_list_in_site = skills + skill_to_remove

now = datetime.now()
current_time = now.strftime("%Y-%m-%d")

# find which companies post on lever
# loop and extract postings related to Sports
# post them if they are not on airtable
# if they are on airtable, update the last updated date MAYBE


response = requests.get(
    f"https://boards-api.greenhouse.io/v1/boards/majorleaguebaseball/jobs?content=true"
)


# decoded = html.unescape(asd.json()["jobs"][0]["content"])
# soup = BeautifulSoup(decoded, "html.parser")
# markdown_text = html_to_markdown(soup)
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
        return country
    else:
        return ""


# Example usage


def html_to_markdown(element):
    if isinstance(element, NavigableString):
        return str(element).strip() + " "
    elif isinstance(element, Tag):
        if element.name == "ul":
            return (
                "\n".join(
                    [f"* {html_to_markdown(item)}" for item in element.find_all("li")]
                )
                + "\n"
            )
        elif element.name == "ol":
            return "\n".join(
                [f"1. {html_to_markdown(item)}" for item in element.find_all("li")]
            )
        else:
            # Recursively process other tags
            return "".join(
                html_to_markdown(child) for child in element.children
            ).strip()
    return ""


companies = {
    "The Score": {
        "greenhouse_name": "scoremediaandgaminginc",
        "logo": [
            {
                "url": "https://v5.airtableusercontent.com/v3/u/26/26/1710619200000/CrE4b7X5KXwig208oUyE2Q/V7bJOwg_FuXZddgUFrVLO69ftDkOX6glWcpWlCQ0lRhbAX7YRAkijtY3sDKdwX-GyIzgqwS8y8JHRZ9-TKpmBGa6fOxh28YzIzhBmiXJ0nieRkY38EhpXPxxI3v3H6TssBgBcRl-y8gNkFMRekovjA/EOvVBtJZZKJBDdMYkM2pwm9Eo_1cSTPFD2TO8TIYnYI",
                "filename": "theScore.png",
            }
        ],
    },
    "Urban Sports Club": {
        "greenhouse_name": "urbansportsclub",
        "logo": [
            {
                "url": "https://s2-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/761/500/resized/1616171296475.jpeg?1633091741",
                "filename": "urban_sports_club.png",
            }
        ],
    },
    "Genius Sports": {
        "greenhouse_name": "geniussports",
        "logo": [
            {
                "url": "https://s3-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/097/300/resized/Logo_genius_1.png?1626023064",
                "filename": "genius_sports.png",
            }
        ],
    },
    "Golden State Warriors": {
        "greenhouse_name": "goldenstatewarriors",
        "logo": [
            {
                "url": "https://v5.airtableusercontent.com/v3/u/26/26/1710626400000/9R1WsQAiPpqQXXGQqSKFPQ/xo79R5POid0LxPPIdb8Y8nAGj2W2C8Ge6aREMCbg6LAqadGZrMxE39Fgi5TesCpd8L3YlEzBnvgizTy8rMO71ylIf8ZoeT1rSMbTPLpv7SCeiuG2MGO7KnhyFKEn61_XGHWvM_H6AGPqPPD23Agn0Q/UMMOVGcpAWpdFYw2Lq7whguhXwRqTDQFnVzv5HLUtQQ",
                "filename": "golden_state_warriors.png",
            }
        ],
    },
    "UnderDog Fantasy": {
        "greenhouse_name": "underdogfantasy",
        "logo": [
            {
                "url": "https://s5-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/278/300/resized/Main_Logo.png?1656375980",
                "filename": "underdog_fantasy.png",
            }
        ],
    },
    "Zelus Analytics": {
        "greenhouse_name": "zelusanalytics",
        "logo": [
            {
                "url": "https://v5.airtableusercontent.com/v3/u/26/26/1710626400000/mndyjFIsAcRfQPyncC47dA/4QsygN3NZnscAjPi8iGy0GHghZNCjj_0p13BYDqBP07Wt-N3Mg1kkxCxXfHi2afryO0RLcujm5y37biLRNrZpwOT67tshkfSoj9JbKbey8WAfQ2wDjytviezqyenYcpuxvsrS77dWPPlis302eRPig/b2yVp7GYv88hMGHyJUj7vna-vCTPIL9Zc4DvRXOVj2c",
                "filename": "zelus_analytics.png",
            }
        ],
    },
    "Barstool Sports": {
        "greenhouse_name": "barstoolsports",
        "logo": [
            {
                "url": "https://www.barstoolsports.com/static/images/logo-white.png",
                "filename": "barstool_sports.png",
            }
        ],
    },
    "Lear Field": {
        "greenhouse_name": "learfield",
        "logo": [
            {
                "url": "https://cdn.learfield.com/wp-content/uploads/2023/12/Learfield_Logo_White-1.png",
                "filename": "lear_field.png",
            }
        ],
    },
    "Excel Sports Management": {
        "greenhouse_name": "excelsportsmanagement",
        "logo": [
            {
                "url": "https://s5-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/440/800/resized/EXCEL_SPORTS_MANAGEMENT__LLC-1553200528-85460.png?1665090576",
                "filename": "excelsportsmanagement.png",
            }
        ],
    },
    "Monumental Sports & Entertainment": {
        "greenhouse_name": "monumentalsports",
        "logo": [
            {
                "url": "https://s7-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/381/000/resized/Monumental-Logo-Large-Light-Background.png?1701188822",
                "filename": "monumental_sports_entertainment.png",
            }
        ],
    },
    "FanDuel": {
        "greenhouse_name": "fanduel",
        "logo": [
            {
                "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAbFBMVEUAce4Ab+4AbO4Aau0AaO0AZu0AZO0ddu55o/Kqw/XG1/ja5fnm7fqzyfYAX+27zvcnee6eu/T///3///xZkfFll/E7gvDD1Pj9//zt8/sAVOz2+fyQsvRAhPDf6PmFqvNunfKauPQAWuwAY+1/YJLWAAABKUlEQVR4Aa2RRaIDIRBEYbDRSDEaHbn/HX9Dx2X1UxvkNVSL+L9korSxSmiVyBeirEuzvCir1TpLN1bJOzJuWwLwHnUDUrl15oJl2xHoSX7YFWHjga5laveIBMDW4Rq3twwHOgL5oaHoY3PIAYIDQ3PyPc7GxDQpaWPO6P3JRKg7gmMilU44iWQk2Om4VxPts7k95GemOqPoSXG2NcGhAJAyXEqC9aUWExLw/fVCtqA9W7IpyYNrM5Vny9u/pC7lhwLXT24mfj2zo+3oUC5MOHcKblTMvQn7kQM5OrbUhSa44F7Yx5FtYseklEns5eZppOpMFFvtIkuVeJKt0Pt83gdWWfGipYMf5jCDjjN9pmvATUDF7JUeMG1wsOKj9LEzrRJfJDU17yf6A4tMGL31Dd89AAAAAElFTkSuQmCC",
                "filename": "fanduel.png",
            }
        ],
    },
    "Swish Analytics": {
        "greenhouse_name": "swishanalytics",
        "logo": [
            {
                "url": "https://s5-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/119/500/resized/Swish-Logo-2023-Black-Square-2.jpg?1693486896",
                "filename": "swish_analytics.png",
            }
        ],
    },
    "Catapult Sports": {
        "greenhouse_name": "catapultsports",
        "logo": [
            {
                "url": "https://recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/000/010/502/resized/Catapult_logo_-_black.png?1634256060",
                "filename": "catapult_sports.png",
            }
        ],
    },
    "Kaizen Gaming": {
        "greenhouse_name": "kaizengaming",
        "logo": [
            {
                "url": "https://productioncms.kaizengaming.com/uploads/header_Logo_b1c17ae784.svg",
                "filename": "kaizen_gaming.png",
            }
        ],
    },
    "The Florida Panthers": {
        "greenhouse_name": "thefloridapanthers",
        "logo": [
            {
                "url": "https://s6-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/048/500/resized/panthers_logo_2.png?1672848760",
                "filename": "florida_panthers.png",
            }
        ],
    },
    "MLB": {
        "greenhouse_name": "majorleaguebaseball",
        "logo": [
            {
                "url": "https://images.ctfassets.net/iiozhi00a8lc/VtQp1Uvhf7RPuqOjXgk2N/3527993b96002b528239944121b9c512/1.svg",
                "filename": "mlb.png",
            }
        ],
    },
    "Second Spectrum": {
        "greenhouse_name": "secondspectrum",
        "logo": [
            {
                "url": "",
                "filename": "second_spectrum.png",
            }
        ],
    },
    "Tempus Ex": {
        "greenhouse_name": "txm",
        "logo": [
            {
                "url": "https://s3-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/014/700/resized/txm-logo.png?1619552318",
                "filename": "tempus_ex.png",
            }
        ],
    },
}

for company, attributes in companies.items():

    response = requests.get(
        f"https://boards-api.greenhouse.io/v1/boards/{attributes['greenhouse_name']}/jobs?content=true"
    )

    for job in response.json()["jobs"]:

        description = job["content"]
        # list_text = ""
        # for list_topics in job["lists"]:

        #     for k, v in list_topics.items():
        #         v = v.replace("<li>", "* ").replace("</li>", "  \n")
        #         list_text += v + "\n"

        # soup = BeautifulSoup(list_text, "html.parser")
        # soup_parsed = soup.get_text()
        decoded = html.unescape(description)
        soup = BeautifulSoup(decoded, "html.parser")

        full_description = f"""{soup.get_text()}"""

        # Just techinical skills we want to filter by
        pattern = r"\b(?:" + "|".join(skills) + r")\b"
        skills_required = [
            skill.lower()
            for skill in set(re.findall(pattern, full_description, re.IGNORECASE))
        ]
        skills_required_format = [
            skill for skill in skills if skill.lower() in skills_required
        ]

        none_skill = len(skills_required) == 0

        if (job["absolute_url"] in recent_urls) or (none_skill):
            continue

        # Duplicate but to add all skills. I should create a function to avoid duplicating.
        pattern = r"\b(?:" + "|".join(skills_to_list_in_site) + r")\b"
        skills_required = [
            skill.lower()
            for skill in set(re.findall(pattern, full_description, re.IGNORECASE))
        ]
        skills_required_format = [
            skill
            for skill in skills_to_list_in_site
            if skill.lower() in skills_required
        ]

        title = job["title"]
        createdAt = job["updated_at"]
        url = job["absolute_url"]
        location = job["location"]["name"]

        country = find_country(location).lower()

        if (
            ("remote" in location.lower())
            | ("remote" in title.lower())
            | ("remote" in full_description.lower())
        ):
            accepts_remote = "Yes"
        else:
            accepts_remote = "No"
        # workplaceType = job["workplaceType"]
        # if workplaceType.upper() == "REMOTE":
        #     accepts_remote = "Yes"
        # else:
        #     accepts_remote = "No"

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

        # hours = job["categories"].get("commitment", "Fulltime")
        hours = "Fulltime"

        if re.search(
            r"\b(?:part time|parttime)\b", title + " " + description, re.IGNORECASE
        ):
            hours = "Part time"

        if hours in [
            "Full-time",
        ]:
            hours = "Fulltime"

        if hours in ["Part-time", "Parttime"]:
            hours = "Part time"

        if hours != "Part time" and hours != "Fulltime":
            hours = "Fulltime"

        record = {
            "Name": title,
            "validated": True,
            "Status": "Open",
            "Start date": current_time,
            "url": url,
            "location": location,
            "country": country,
            "seniority": seniority,
            "desciption": full_description,
            "skills": skills_required_format,
            "remote": accepts_remote,
            "salary": None,
            "language": ["English"],
            "company": company,
            "type": ["Permanent"],
            "hours": [hours],
            "logo": attributes.get("logo", []),
            "SEO:Index": "1",
        }
        table.create(record)
