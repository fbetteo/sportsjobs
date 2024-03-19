import requests
from bs4 import BeautifulSoup


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

now = datetime.now()
current_time = now.strftime("%Y-%m-%d")

# find which companies post on lever
# loop and extract postings related to Sports
# post them if they are not on airtable
# if they are on airtable, update the last updated date MAYBE
from urllib.request import urlopen
import re as r


def getIP():
    d = str(urlopen("http://checkip.dyndns.com/").read())

    return r.compile(r"Address: (\d+\.\d+\.\d+\.\d+)").search(d).group(1)


IP = getIP()


for country_id in [5039, 5040, 5041, 5042, 5043, 5044]:
    print(country_id)

    country_map = {
        5039: "united states",
        5040: "united kingdom",
        5041: "germany",
        5042: "australia",
        5043: "canada",
        5044: "india",
    }

    parameters = {
        "publisher": country_id,
        "user_ip": IP,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "keyword": "sports analytics",
        "limit": 50,
    }

    # Set URL
    # url = '/api/jobs.xml?%s' % urllib.urlencode(parameters)

    # Exec and return the result
    response = requests.get(
        "https://api.whatjobs.com/api/v1/jobs.json", params=parameters
    )

    for job in response.json()["data"]:

        description = job["snippet"]
        list_text = description.replace("<li>", "* ").replace("</li>", "  \n")

        soup = BeautifulSoup(list_text, "html.parser")
        soup_parsed = soup.get_text()

        pattern = r"\b(?:" + "|".join(skills) + r")\b"
        skills_required = [
            skill.lower()
            for skill in set(re.findall(pattern, soup_parsed, re.IGNORECASE))
        ]
        skills_required_format = [
            skill for skill in skills if skill.lower() in skills_required
        ]

        none_skill = len(skills_required) == 0

        if (job["url"] in recent_urls) or (none_skill) or (job["age_days"] > 40):
            continue

        title = job["title"]
        createdAt = job["age"]
        url = job["url"]
        location = job["location"]
        country = country_map[country_id]
        # I don't know how REMOTE positions appear. Putting this as default
        workplaceType = job["location"]
        if workplaceType.upper() == "REMOTE":
            accepts_remote = "Yes"
        else:
            accepts_remote = "No"

        if re.search(
            r"\b(?:intern|internship|internships)\b",
            title + " " + soup_parsed,
            re.IGNORECASE,
        ):
            seniority = "Internship"
        elif re.search(r"\b(?:junior)\b", title + " " + soup_parsed, re.IGNORECASE):
            seniority = "Junior"
        else:
            seniority = "With Experience"

        record = {
            "Name": title,
            "validated": True,
            "Status": "Open",
            "Start date": current_time,
            "url": url,
            "location": location,
            "country": country,
            "seniority": seniority,
            "desciption": soup_parsed,
            "skills": skills_required_format,
            "remote": accepts_remote,
            "salary": None,
            "language": ["English"],
            "company": job["company"],
            "type": ["Permanent"],
            "hours": ["Fulltime"],
            "logo": [],
            "SEO:Index": "1",
        }
        table.create(record)


# playonsports
# brooksrunning
# Kickoff
# gametime
# sportalliance EU


# playon = requests.get(f"https://api.lever.co/v0/postings/playonsports")

# brooksrunning = requests.get(f"https://api.lever.co/v0/postings/brooksrunning")

# kickoff = requests.get(f"https://api.lever.co/v0/postings/Kickoff")

# game_time = requests.get(f"https://api.lever.co/v0/postings/gametime")

# sportalliance = requests.get(f"https://api.eu.lever.co/v0/postings/sportalliance")

# ##
# fancode = requests.get(f"https://api.lever.co/v0/postings/dreamsports")

# grundens = requests.get(f"https://api.lever.co/v0/postings/Grundens")

# sporty = requests.get(f"https://api.lever.co/v0/postings/sporty")

# betr = requests.get(f"https://api.lever.co/v0/postings/betr")


# kitmanlabs = requests.get(f"https://api.lever.co/v0/postings/kitmanlabs")

# fnatic = requests.get(f"https://api.lever.co/v0/postings/fnatic")

# crossfit = requests.get(f"https://api.lever.co/v0/postings/crossfit")

# betstamp = requests.get(f"https://api.lever.co/v0/postings/Betstamp")
