from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [ "https://www.googleapis.com/auth/indexing" ]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# service_account_file.json is the private key that you created for your service account.
JSON_KEY_FILE = "C:/Users/Franco/Downloads/sportsjobs-81587141c98e.json"

credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)


import os
from pyairtable import Api
import requests.auth
from dotenv import load_dotenv, find_dotenv
os.getcwd()

load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/redditbot/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")


api = Api(AIRTABLE_TOKEN)



table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)
all = table.all(sort = ['-creation_date'], max_records = 100)


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
