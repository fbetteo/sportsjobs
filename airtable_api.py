import os
from pyairtable import Api
import requests
import requests.auth
import time
import json

# from dotenv import load_dotenv, find_dotenv

os.getcwd()

# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/sportsjobs/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")


REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASS = os.getenv("REDDIT_PASS")
SUBREDDIT = os.getenv("SUBREDDIT")
SUBREDDIT_DISPLAY_NAME = os.getenv("SUBREDDIT_DISPLAY_NAME")

REDDIT_CLIENT = os.getenv("REDDIT_CLIENT")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")


api = Api(AIRTABLE_TOKEN)


table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)
all = table.all(sort=["-creation_date"], max_records=30)


with open("latest_posted.json", "r") as f:
    data = json.load(f)


# unlock are the hook for free users
# random < 25 is the rule I have in airtable for the free view. I just want to post the free tier jobs
latest_jobs = [
    row
    for row in all
    if (row["fields"]["creation_date"] > data["creation_date"])
    and (row["fields"]["Name"] != "Unlock this job")
    and (row["fields"]["random"] < 25)
]

# post to reddit

# username = REDDIT_USERNAME
# subreddit = SUBREDDIT
# subreddit_display_name = SUBREDDIT_DISPLAY_NAME

client_auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT, REDDIT_SECRET)
post_data = {
    "grant_type": "password",
    "username": REDDIT_USERNAME,
    "password": REDDIT_PASS,
}
headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}
response = requests.post(
    "https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data
)
response.json()

access_token = response.json()["access_token"]
token_type = response.json()["token_type"]

# posting in my community sportsjobs_online
for job in latest_jobs[::-1]:
    post_data = {
        "title": job["fields"]["Name"] + " - " + job["fields"]["company"],
        "kind": "link",
        "sr": SUBREDDIT,
        "url": job["fields"]["job_detail_url"]
        + f"?utm_source=reddit&utm_medium=bot_{SUBREDDIT}",
        "resubmit": "true",
        "api_type": "json",
        "sendreplies": "true",
        "text": job["fields"]["desciption"],
    }

    requests.post(
        "https://oauth.reddit.com/api/submit",
        headers={
            "Authorization": "bearer " + access_token,
            "User-Agent": "ChangeMeClient/0.1 by YourUsername",
        },
        data=post_data,
    )
    time.sleep(1)


# to check if there was an actual update
if job:
    # update latest_posted.json
    latest_posted = {"id": job["id"], "creation_date": job["fields"]["creation_date"]}
    # overwrite to json file
    with open("latest_posted.json", "w") as f:
        json.dump(latest_posted, f)


for job in latest_jobs[::-1]:
    if job["fields"]["remote"] == "Yes":

        post_data = {
            "title": "[HIRING] " + job["fields"]["Name"],
            "kind": "link",
            "sr": "workremotely",
            "url": job["fields"]["job_detail_url"]
            + f"?utm_source=reddit&utm_medium=bot_workremotely",
            "resubmit": "true",
            "api_type": "json",
            "sendreplies": "true",
            "text": job["fields"]["desciption"],
        }

        requests.post(
            "https://oauth.reddit.com/api/submit",
            headers={
                "Authorization": "bearer " + access_token,
                "User-Agent": "ChangeMeClient/0.1 by YourUsername",
            },
            data=post_data,
        )
        time.sleep(1)
