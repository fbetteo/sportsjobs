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

companies = {
    "The Athletic": {
        "lever_name": "theathletic",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/8ff13c41-d891-40d4-b9d8-de9c995ff06f-1600385441351.png",
                "filename": "theathletic.png",
            }
        ],
    },
    "PlayOn! Sports": {
        "lever_name": "playonsports",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/41a41462-61a1-46dd-9190-73fd66fa11ee-1656096708496.png",
                "filename": "playonsports.png",
            }
        ],
    },
    "Brooks Running": {
        "lever_name": "brooksrunning",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.amazonaws.com/f0a2961a-09a7-412e-9b8f-0d186769bc1a-1501529042183.png",
                "filename": "brooksrunning.png",
            }
        ],
    },
    "Kickoff": {
        "lever_name": "Kickoff",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/537a8842-2bd0-43b4-bb27-fc6c26450c29-1706218622648.png",
                "filename": "kickoff.png",
            }
        ],
    },
    "GameTime": {
        "lever_name": "gametime",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.amazonaws.com/a0ca3046-353c-409d-bf49-22a954da734a-1568149219931.png",
                "filename": "gametime.png",
            }
        ],
    },
    "SportAlliance": {"lever_name": "sportalliance", "logo": [], "europe": True},
    "Dream Sports": {
        "lever_name": "dreamsports",
        "logo": [
            {
                "url": "https://lever-client-logos.s3-us-west-2.amazonaws.com/58d80c3e-b78b-4751-b256-c1dd090370f2-1588151685110.png",
                "filename": "dreamsports.png",
            }
        ],
    },
    "Grundens": {
        "lever_name": "Grundens",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/c7c1d8a4-cf7f-459f-8422-96ab19215b0f-1612978037834.png",
                "filename": "grundens.png",
            }
        ],
    },
    "Sporty": {
        "lever_name": "sporty",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/6616a346-760f-4098-a325-0a582aa0542e-1608646767819.png",
                "filename": "sporty.png",
            }
        ],
    },
    "Betr": {
        "lever_name": "betr",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/56f26027-121f-4868-938c-ba9bdef5c57c-1658709755202.png",
                "filename": "betr.png",
            }
        ],
    },
    "Kitman Labs": {
        "lever_name": "kitmanlabs",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/00b27a9e-32b0-4248-b224-5147ecacd464-1688118163729.png",
                "filename": "kitmanlabs.png",
            }
        ],
    },
    "Fnatic": {
        "lever_name": "fnatic",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.amazonaws.com/80d1f71b-c66f-4193-8bb1-85dfda9a629e-1580903456170.png",
                "filename": "fnatic.png",
            }
        ],
    },
    "CrossFit": {
        "lever_name": "crossfit",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/7744085c-b7f6-4d4a-b5b2-9f310e0bb564-1646405943505.png",
                "filename": "crossfit.png",
            }
        ],
    },
    "Decathlon": {
        "lever_name": "decathlon",
        "logo": [
            {
                "url": "https://lever-client-logos.s3-us-west-2.amazonaws.com/96301246-02ad-40a1-92bf-2bd7cc356619-1595317253089.png",
                "filename": "decathlon.png",
            }
        ],
    },
    "Tactical": {
        "lever_name": "tactical",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/536e5a0b-3b30-4a95-8eb4-104733be2bed-1695288810431.png",
                "filename": "tactical.png",
            }
        ],
    },
    "Therabody": {
        "lever_name": "therabodycorp",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/bda14eb5-db87-42eb-bff3-8f519839d998-1694110621453.png",
                "filename": "therabody.png",
            }
        ],
    },
    "Red Sox": {
        "lever_name": "redsox",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/3fcd8203-00a9-4862-af38-f4319bcd5502-1632854624658.png",
                "filename": "redsox.png",
            }
        ],
    },
    "Fanatics": {
        "lever_name": "fanatics",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.amazonaws.com/a26ea84a-d8a3-4394-9927-2b0243d2df5a-1552380484471.png",
                "filename": "fanatics.png",
            }
        ],
    },
    "Fliff": {
        "lever_name": "Fliff",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/bdcc0bbf-00c2-4894-963a-34ee45ec4151-1682980316341.png",
                "filename": "fliff.png",
            }
        ],
    },
    "Veo": {
        "lever_name": "veo",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/83bd9f2d-6d1b-4436-9fdd-5472b25ec1cd-1696251305225.png",
                "filename": "veo.png",
            }
        ],
    },
    "Dazn": {
        "lever_name": "dazn",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.amazonaws.com/53e8aff7-f3d4-4c1b-9e27-d738a16ea713-1550137638864.png",
                "filename": "dazn.png",
            }
        ],
    },
    "Winamax": {
        "lever_name": "winamax",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/71117a08-0c6c-499d-aa39-5464ddde795c-1671709110651.png",
                "filename": "winamax.png",
            }
        ],
    },
    "Nemesis Corporation": {
        "lever_name": "nemesiscorporation",
        "logo": [
            {
                "url": "",
                "filename": "nemesis.png",
            }
        ],
    },
    "Luni": {
        "lever_name": "luni",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/c0367655-c9e3-4700-996c-b2f3fd130ba9-1657619706201.png",
                "filename": "luni.png",
            }
        ],
    },
    "Legend": {
        "lever_name": "Legend",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/7215073c-e908-41d8-a877-4199bc726c98-1698847110583.png",
                "filename": "legend.png",
            }
        ],
    },
    "Catena Media": {
        "lever_name": "catenamedia",
        "logo": [
            {
                "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/497dbfe7-452f-4344-98bd-8610d270084d-1599066587951.png",
                "filename": "catenamedia.png",
            }
        ],
    },
    # "Betstamp": {
    #     "lever_name": "Betstamp",
    #     "logo": [
    #         {
    #             "url": "https://lever-client-logos.s3.us-west-2.amazonaws.com/ccfa9849-85c7-4334-994a-e2eb3f913c54-1633288684940.png",
    #             "filename": "betstamp.png",
    #         }
    #     ],
    # },
}

for company, attributes in companies.items():

    if not attributes.get("europe", False):
        response = requests.get(
            f"https://api.lever.co/v0/postings/{attributes['lever_name']}"
        )
    else:
        response = requests.get(
            f"https://api.eu.lever.co/v0/postings/{attributes['lever_name']}"
        )

    for job in response.json():

        description = job["descriptionPlain"]
        list_text = ""
        for list_topics in job["lists"]:

            for k, v in list_topics.items():
                v = v.replace("<li>", "* ").replace("</li>", "  \n")
                list_text += v + "\n"

        soup = BeautifulSoup(list_text, "html.parser")
        soup_parsed = soup.get_text()

        full_description = f"""{description} 
          {soup_parsed}"""

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

        if (job["hostedUrl"] in recent_urls) or (none_skill):
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

        title = job["text"]
        createdAt = job["createdAt"]
        url = job["hostedUrl"]
        location = job["categories"]["allLocations"]
        raw_country = job["country"]

        country_map = {
            "us": "united states",
            "uk": "united kingdom",
            "de": "germany",
            "fr": "france",
            "es": "spain",
            "it": "italy",
            "nl": "netherlands",
            "se": "sweden",
            "dk": "denmark",
            "fi": "finland",
            "no": "norway",
            "be": "belgium",
            "at": "austria",
            "ch": "switzerland",
            "ie": "ireland",
            "pl": "poland",
            "pt": "portugal",
            "cz": "czech republic",
            "gr": "greece",
            "sa": "saudi arabia",
            "ae": "united arab emirates",
            "ca": "canada",
            "jo": "jordan",
            "br": "brazil",
            "au": "australia",
            "nz": "new zealand",
            "in": "india",
            "sg": "singapore",
            "hk": "hong kong",
            "jp": "japan",
            "cn": "china",
            "kr": "south korea",
            "gb": "united kingdom",
            "th": "thailand",
            "mt": "malta",
            "ua": "ukraine",
            "bg": "bulgaria",
            "je": "jersey",
            "ar": "argentina",
        }

        try:
            country = country_map.get(raw_country.lower(), raw_country.lower())
        except:
            country = ""

        workplaceType = job["workplaceType"]
        if workplaceType.upper() == "REMOTE":
            accepts_remote = "Yes"
        else:
            accepts_remote = "No"

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

        hours = job["categories"].get("commitment", "Fulltime")

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
            "location": location[0],
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
