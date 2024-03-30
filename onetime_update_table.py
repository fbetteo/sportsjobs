# Update AIRTABLE FIELDS

import requests
from bs4 import BeautifulSoup


import os
from pyairtable import Api
import requests
import requests.auth
import re
from dotenv import load_dotenv, find_dotenv

from utils import is_remote_global, add_sport_list

os.getcwd()

# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/redditbot/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")

api = Api(AIRTABLE_TOKEN)
table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)


all = table.all()


def add_job_area(skills):
    skills = " ".join(skills)  # Convert list to string
    if re.search(r"Data Engineer|Data Engineering|ETL", skills):
        return "Data Engineer"
    elif re.search(r"Data Science|Data Scientist|Machine Learning", skills):
        return "DS/ML/AI"
    else:
        return "Analytics"


# for row in all:
#     sport_list = add_sport_list(row["fields"]["desciption"])
#     table.update(row["id"], {'sport_list': sport_list})


# for row in all:
#     industry = add_industry(row["fields"]["desciption"])
#     table.update(row["id"], {'industry': industry})


# for row in all:
#     industry = add_job_area(row["fields"]["skills"])
#     table.update(row["id"], {'job_area': add_job_area})

for row in all:
    remote_office = is_remote_global(
        row["fields"]["desciption"]
        + " "
        + row["fields"]["Name"]
        + " "
        + row["fields"].get("location", "")
    )
    table.update(row["id"], {"remote_office": remote_office})
