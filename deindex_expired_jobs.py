import json
from typing import Mapping, Optional

from hetzner_utils import (
    start_postgres_connection,
    get_expired_jobs,
)

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
JSON_KEY_FILE = "./sportsjobs-v2-key.json"
SITE_URL = "https://www.sportsjobs.online"


def build_update_notification(job: Mapping[str, object]) -> Optional[dict[str, str]]:
    """Build the canonical Indexing API update for an expired job."""
    slug = str(job.get("slug") or "").strip()
    if not slug:
        return None

    return {
        "url": f"{SITE_URL}/jobs/{slug}",
        "type": "URL_UPDATED",
    }


def main() -> None:
    import httplib2
    from oauth2client.service_account import ServiceAccountCredentials

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        JSON_KEY_FILE, scopes=SCOPES
    )
    conn = start_postgres_connection()

    try:
        with conn:
            for job in get_expired_jobs(conn):
                notification = build_update_notification(job)
                if notification is None:
                    print(
                        "Skipping expired job without a canonical slug: "
                        f"job_id={job.get('job_id')}"
                    )
                    continue

                http = credentials.authorize(httplib2.Http())
                response, _ = http.request(
                    ENDPOINT,
                    method="POST",
                    body=json.dumps(notification),
                    headers={"Content-Type": "application/json"},
                )
                print(
                    f"Google Indexing API status={response.status} "
                    f"url={notification['url']}"
                )

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if conn and conn.closed == 0:
            conn.close()
            print("Connection closed.")


if __name__ == "__main__":
    main()
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
