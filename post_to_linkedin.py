import os
import requests
from datetime import datetime
from hetzner_utils import start_postgres_connection

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_COMPANY_ID = os.getenv("LINKEDIN_COMPANY_ID")

HEADERS_LINKEDIN = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

conn = start_postgres_connection()

try:
    with conn as conn:
        # Get today's jobs from postgres
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT name, company, country 
            FROM jobs 
            WHERE DATE(start_date) = %s
            """,
            (today,)
        )
        todays_jobs = cursor.fetchall()

        # Post each job to LinkedIn
        for job in todays_jobs:
            job_title, company, country = job
            post_text = f"""
            New job in sports analytics!

            🏀⚽🏈 {job_title} - {company} - {country.capitalize()}

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
                "https://api.linkedin.com/v2/ugcPosts", 
                headers=HEADERS_LINKEDIN, 
                json=content
            )
            print(response.status_code, response.json())

except Exception as e:
    print(f"Error occurred: {e}")
finally:
    # Ensure the connection is closed if still open
    if conn and conn.closed == 0:
        conn.close()
        print("Connection closed.")