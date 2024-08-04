### Ashbyhq

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
import markdownify
from utils import (
    is_remote_global,
    add_job_area,
    search_for_png_image,
    extract_salary,
    find_country,
)

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

# skill_to_remove = [
#     "Data",
#     "Media",
#     "IT",
#     "Sports",
#     "Manager",
#     "Gaming",
#     "Social Media",
#     "baseball",
#     "kpi",
#     "Networks",
#     "Excel",
#     "Powerpoint",
#     "Analytics",
#     "Statistics",
# ]

# for skill in skill_to_remove:
#     skills.remove(skill)

# skills_to_list_in_site = skills + skill_to_remove


skills_to_search = [
    "Devops",
    "Machine Learning",
    "Data Science",
    "Data Scientist",
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
]


skills = skills + skills_to_search


now = datetime.now()
current_time = now.strftime("%Y-%m-%d")

# find which companies post on lever
# loop and extract postings related to Sports
# post them if they are not on airtable
# if they are on airtable, update the last updated date MAYBE


# response = requests.get(
#     f"https://api.ashbyhq.com/posting-api/job-board/sleeper?includeCompensation=true"
# )


# response.json()["jobs"][0]


# decoded = html.unescape(asd.json()["jobs"][0]["content"])
# soup = BeautifulSoup(decoded, "html.parser")
# markdown_text = html_to_markdown(soup)
# def clean_location(location):
#     location = location.lower()
#     location = location.split("/")[0]
#     location = location.split("-")[0]
#     location = location.split("or")[0]
#     location = location.replace("remote", "")
#     location = location.replace("hybrid", "")
#     location = location.replace("in office", "")
#     return location


# def find_country(location_str):
#     location_str = clean_location(location_str)
#     geolocator = Nominatim(user_agent="sportsjobs")
#     location = geolocator.geocode(
#         location_str, exactly_one=True, addressdetails=True, language="en"
#     )

#     if location:
#         # Access the address dictionary
#         address = location.raw.get("address", {})
#         # Get the country
#         country = address.get("country", "Country not found")
#         return country
#     else:
#         return "united states"


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
    "Sleeper": {
        "name": "sleeper",
        "logo": [
            {
                "url": "https://app.ashbyhq.com/api/images/org-theme-wordmark/4e79ba20-10c6-4335-954a-b0917a08a1d1/5b880aa8-8278-4da5-8eef-4b88b172ffc9.png",
                "filename": "sleeper.png",
            }
        ],
    },
    "Hawk-Eye Innovations": {
        "name": "hawkeyeinnovations",
        "logo": [
            {
                "url": "https://app.ashbyhq.com/api/images/org-theme-wordmark/4f986611-16b6-40b0-a7c5-f32d9f756a83/05af0471-fb28-42f9-a8f8-3d31bea1a45a.png",
                "filename": "hawk-eye-innovations.png",
            }
        ],
    },
    "Sorare": {
        "name": "Sorare",
        "logo": [
            {
                "url": "https://app.ashbyhq.com/api/images/org-theme-wordmark/04de55dd-d142-4ba7-ba52-70b026fe4c90/319269e8-b78f-4df7-927f-8213f12d757d.png",
                "filename": "sorare.png",
            }
        ],
    },
    "GameChanger": {
        "name": "gamechanger",
        "logo": [],
    },
}

for company, attributes in companies.items():

    response = requests.get(
        f"https://api.ashbyhq.com/posting-api/job-board/{attributes['name']}?jobsincludeCompensation=true"
    )

    if response.status_code != 200:
        continue
    for job in response.json()["jobs"]:

        description = job["descriptionHtml"]
        # list_text = ""
        # for list_topics in job["lists"]:

        #     for k, v in list_topics.items():
        #         v = v.replace("<li>", "* ").replace("</li>", "  \n")
        #         list_text += v + "\n"

        # soup = BeautifulSoup(list_text, "html.parser")
        # soup_parsed = soup.get_text()
        # decoded = html.unescape(description)
        # soup = BeautifulSoup(decoded, "html.parser")

        # full_description = f"""{soup.get_text()}"""
        # full_description = description
        full_description = markdownify.markdownify(description, heading_style="ATX")

        # Just techinical skills we want to filter by
        pattern = r"\b(?:" + "|".join(skills_to_search) + r")\b"
        skills_required = [
            skill.lower()
            for skill in set(
                re.findall(
                    pattern, full_description + " " + job["title"], re.IGNORECASE
                )
            )
        ]
        skills_required_format = [
            skill for skill in skills if skill.lower() in skills_required
        ]

        none_skill = len(skills_required) < 2

        if (job["jobUrl"] in recent_urls) or (none_skill):
            continue

        # Duplicate but to add all skills. I should create a function to avoid duplicating.
        pattern = r"\b(?:" + "|".join(skills) + r")\b"
        skills_required = [
            skill.lower()
            for skill in set(
                re.findall(
                    pattern, full_description + " " + job["title"], re.IGNORECASE
                )
            )
        ]
        skills_required_format = [
            skill for skill in skills if skill.lower() in skills_required
        ]

        title = job["title"]
        createdAt = job["publishedAt"]
        url = job["jobUrl"]
        location = job["location"]

        country = find_country(location)["country"]
        country_code = find_country(location)["country_code"]

        if (
            ("remote" in location.lower())
            | ("remote" in title.lower())
            | ("remote" in full_description.lower())
        ):
            accepts_remote = "Yes"
        else:
            accepts_remote = "No"

        if job["isRemote"]:
            accepts_remote = "Yes"
        # workplaceType = job["workplaceType"]
        # if workplaceType.upper() == "REMOTE":
        #     accepts_remote = "Yes"
        # else:
        #     accepts_remote = "No"
        remote_office = is_remote_global(full_description)

        job_area = add_job_area(skills_required_format)

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
        hours = job.get("employmentType", "Fulltime")

        if re.search(
            r"\b(?:part time|parttime)\b", title + " " + description, re.IGNORECASE
        ):
            hours = "Part time"

        if hours in ["Full-time", "FullTime"]:
            hours = "Fulltime"

        if hours in ["Part-time", "Parttime"]:
            hours = "Part time"

        if hours != "Part time" and hours != "Fulltime":
            hours = "Fulltime"
        # CHANGE THIS FOR GET_HOURS IN UTILS. I'M WORKING ON ANOTHER THING BUT I SHOULD CHECK THIS

        # Industry
        industry = []
        if re.search(
            r"\b(?:sports betting|betting|gambling)\b",
            title + " " + description,
            re.IGNORECASE,
        ):
            industry += ["Betting"]
        elif re.search(
            r"\b(?:esports|esport)\b", title + " " + description, re.IGNORECASE
        ):
            industry += ["Esports"]
        else:
            industry += ["Sports"]

        # Sport
        sport_list = []
        if re.search(
            r"\b(?:basketball|nba)\b",
            title + " " + description,
            re.IGNORECASE,
        ):
            sport_list += ["Basketball"]
        elif re.search(
            r"\b(?:football|NFL)\b", title + " " + description, re.IGNORECASE
        ):
            sport_list += ["Football"]
        elif re.search(
            r"\b(?:football|soccer|MLS)\b", title + " " + description, re.IGNORECASE
        ):
            sport_list += ["Football"]
        elif re.search(
            r"\b(?:baseball|MLB)\b", title + " " + description, re.IGNORECASE
        ):
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

        logo = attributes.get("logo", [])
        if len(logo) == 0:
            google_logo = search_for_png_image(company)
            if google_logo:
                logo = google_logo
            else:
                logo = []

        if len(logo) > 0:
            logo_permanent_url = logo[0]["url"]
        else:
            logo_permanent_url = ""

        try:
            salary = extract_salary(full_description)[0]
        except:
            salary = None

        record = {
            "Name": title,
            "validated": True,
            "Status": "Open",
            "Start date": current_time,
            "url": url,
            "location": location,
            "country": country,
            "counrty_code": country_code,
            "seniority": seniority,
            "desciption": full_description,
            "sport_list": sport_list,
            "skills": skills_required_format,
            "remote": accepts_remote,
            "remote_office": remote_office,
            "job_area": job_area,
            "salary": salary,
            "language": ["English"],
            "company": company,
            "industry": industry,
            "type": ["Permanent"],
            "hours": [hours],
            "logo": logo,
            "logo_permanent_url": logo_permanent_url,
            "SEO:Index": "1",
        }
        table.create(record)
