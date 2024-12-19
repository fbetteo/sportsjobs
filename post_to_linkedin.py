import os

from pyairtable import Api
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# from dotenv import load_dotenv, find_dotenv


# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/sportsjobs/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_COMPANY_ID = os.getenv("LINKEDIN_COMPANY_ID")

api = Api(AIRTABLE_TOKEN)

# # JOBS
table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)
today = datetime.now().strftime("%Y-%m-%d")  # Format to ISO format for better filtering

# Adjust filter formula to compare the formatted start date
# Convert Airtable's "Start date" to an ISO date string for comparison
records = table.all(
    formula=f"DATETIME_FORMAT({{Start date}}, 'YYYY-MM-DD') = '{today}'"
)

HEADERS_LINKEDIN = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


for record in records:
    job_title = record["fields"].get("Name", "New Job")
    company = record["fields"].get("company", "Company")
    country = record["fields"].get("country", "country").capitalize()
    post_text = f"""
    New job in sports analytics!

    🏀⚽🏈 {job_title} - {company} - {country}

    Apply and find more opportunities here: www.sportsjobs.online  
    Follow us for more job opportunities in sports analytics!
    """

    content = {
        "author": f"urn:li:organization:{LINKEDIN_COMPANY_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text.strip()},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    response = requests.post(
        "https://api.linkedin.com/v2/ugcPosts", headers=HEADERS_LINKEDIN, json=content
    )
    print(response.status_code, response.json())
