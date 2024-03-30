from oauth2client.service_account import ServiceAccountCredentials
import httplib2

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# service_account_file.json is the private key that you created for your service account.
JSON_KEY_FILE = "D:/DataScience/sportsjobs/sportsjobs-81587141c98e.json"

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    JSON_KEY_FILE, scopes=SCOPES
)


import os
from pyairtable import Api
import requests.auth
from dotenv import load_dotenv, find_dotenv

os.getcwd()

# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/sportsjobs/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")
AIRTABLE_BLOG_TABLE = os.getenv("AIRTABLE_BLOG_TABLE")


api = Api(AIRTABLE_TOKEN)

# JOBS
table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)
all = table.all(sort=["-creation_date"], max_records=20)


for job in all:
    http = credentials.authorize(httplib2.Http())

    # Define contents here as a JSON string.
    # This example shows a simple update request.
    # Other types of requests are described in the next step.
    # print(f"""{{
    # "url": {job['fields']['job_detail_url']},
    # "type": "URL_UPDATED"
    # }}""")
    content = f"""{{
    "url": "{job['fields']['job_detail_url']}",
    "type": "URL_UPDATED"
    }}"""

    response, content = http.request(ENDPOINT, method="POST", body=content)


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
#     "url": "{job['fields']['job_detail_url']}",
#     "type": "URL_DELETED"
#     }}"""

#     response, content = http.request(ENDPOINT, method="POST", body=content)


# IF("Data Engineer" | "Data Engineering" | "ETL" in skills, "Data Engineer",
# IF("Data Science" | "Data Scientist" | "Machine Learning") in skills, "DS/ML/AI", "Analytics")
