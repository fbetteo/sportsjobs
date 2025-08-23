from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import json
import requests

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# service_account_file.json is the private key that you created for your service account.
JSON_KEY_FILE = "./sportsjobs-v2-key.json"

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    JSON_KEY_FILE, scopes=SCOPES
)


import os

# from pyairtable import Api
import requests.auth
from dotenv import load_dotenv, find_dotenv
from hetzner_utils import (
    start_postgres_connection,
    get_recent_urls,
    get_skills,
    insert_records,
    get_recent_jobs,
)

os.getcwd()


def submit_to_indexnow(urls, api_key, host):
    """Submits a list of URLs to the IndexNow API."""
    if not urls:
        print("No URLs to submit to IndexNow.")
        return

    endpoint = "https://api.indexnow.org/IndexNow"
    payload = {
        "host": host,
        "key": api_key,
        "urlList": urls,
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()  # Raises an exception for bad status codes
        print(f"IndexNow submission successful. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error submitting to IndexNow: {e}")


# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/sportsjobs/.env"))
load_dotenv(find_dotenv())

# AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
# AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
# AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")
# AIRTABLE_BLOG_TABLE = os.getenv("AIRTABLE_BLOG_TABLE")
INDEXNOW_API_KEY = os.getenv("INDEXNOW_API_KEY")
INDEXNOW_HOST = os.getenv("INDEXNOW_HOST")


# api = Api(AIRTABLE_TOKEN)

# # JOBS
# table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)
# all = table.all(sort=["-creation_date"], max_records=20)
conn = start_postgres_connection()

try:
    with conn as conn:
        latest_jobs = get_recent_jobs(conn)
        urls_to_submit = []

        for job in latest_jobs:
            url = f"https://www.sportsjobs.online/jobs/{job['slug']}"
            urls_to_submit.append(url)

            # Google Indexing API submission
            http = credentials.authorize(httplib2.Http())
            content = json.dumps({"url": url, "type": "URL_UPDATED"})
            response, response_content = http.request(
                ENDPOINT, method="POST", body=content
            )
            print(f"Google Indexing API Status: {response.status}")

        # Bing IndexNow API submission
        if INDEXNOW_API_KEY and INDEXNOW_HOST:
            submit_to_indexnow(urls_to_submit, INDEXNOW_API_KEY, INDEXNOW_HOST)
        else:
            print(
                "IndexNow API key or host not found in environment variables. Skipping submission."
            )


except Exception as e:
    print(f"Error occurred: {e}")
finally:
    # Ensure the connection is closed if still open
    if conn and conn.closed == 0:
        conn.close()
        print("Connection closed.")
# # BLOG
# table = api.table(AIRTABLE_BASE, AIRTABLE_BLOG_TABLE)
# all = table.all(sort=["-creation_date"], max_records=1)


# for job in all:
#     http = credentials.authorize(httplib2.Http())

#     # Define contents here as a JSON string.
#     # This example shows a simple update request.
#     # Other types of requests are described in the next step.
#     # print(f"""{{
#     # "url": {job['fields']['job_detail_url']},
#     # "type": "URL_UPDATED"
#     # }}""")
#     content = f"""{{
#     "url": "{job['fields']['blog_post_url']}",
#     "type": "URL_UPDATED"
#     }}"""

#     response, content = http.request(ENDPOINT, method="POST", body=content)


# # Deleteing batch of URL from deleted_jobd view
# import requests
# access_token = "pathar3UoJ0PrdpIE.700c76038885c1b2cf7226e530aa46c551257268bcdb4f3c3d68f2bebe5e8db2"
# headers = {"Authorization": "Bearer " + access_token}
# result = requests.get(
#         "https://api.airtable.com/v0/app61I7CwlK0gHEIX/jobs?view=deleted_jobs",
#         headers=headers,
#     )

# for job in result.json()['records']:
#     http = credentials.authorize(httplib2.Http())

#     # Define contents here as a JSON string.
#     # This example shows a simple update request.
#     # Other types of requests are described in the next step.
#     # print(f"""{{
#     # "url": {job['fields']['job_detail_url']},
#     # "type": "URL_UPDATED"
#     # }}""")
#     content = f"""{{
#     "url": "{job['fields']['new_job_url']}",
#     "type": "URL_DELETED"
#     }}"""

#     response, content = http.request(ENDPOINT, method="POST", body=content)


# IF("Data Engineer" | "Data Engineering" | "ETL" in skills, "Data Engineer",
# IF("Data Science" | "Data Scientist" | "Machine Learning") in skills, "DS/ML/AI", "Analytics")
