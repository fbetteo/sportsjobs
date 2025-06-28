# send marketing mail
import resend
import os

from pyairtable import Api
import time
import json

import pandas as pd
import numpy as np
from hetzner_utils import (
    start_postgres_connection,
    get_recent_urls,
    get_skills,
    insert_records,
    get_recent_jobs,
    get_recent_jobs_df,
    get_table,
)

# from dotenv import load_dotenv, find_dotenv


# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/sportsjobs/.env"))

# AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
# AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
# AIRTABLE_ALERTS_TABLE = os.getenv("AIRTABLE_ALERTS_TABLE")
# AIRTABLE_USERS_TABLE = os.getenv("AIRTABLE_USERS_TABLE")
# AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")

resend.api_key = os.environ["RESEND_API_KEY"]

# api = Api(AIRTABLE_TOKEN)


# alerts_table = api.table(AIRTABLE_BASE, AIRTABLE_ALERTS_TABLE).all()
# users_table = api.table(AIRTABLE_BASE, AIRTABLE_USERS_TABLE).all()
# jobs_table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE).all()

from datetime import datetime, timedelta

feedback_form_url = "https://tally.so/r/me8PMx"
review_form_url = "https://senja.io/p/sportsjobs-online/r/63JNc2"

html_body = f"""
<div>
<body style="font-family: Arial, sans-serif; background-color: #f6f6f6; padding: 30px;">
    <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
      
      <h2 style="color: #0066cc; text-align: center;">Thanks for being part of SportsJobs Online 🙌</h2>
      
      <p style="font-size: 16px; color: #333;">Hi,</p>
      
      <p style="font-size: 16px; color: #333;">
        We'd love to hear your thoughts on how things are going. Whether you found a job, are still searching, or just exploring — your feedback helps us improve and connect more people with opportunities in sports analytics.
      </p>

      <p style="font-size: 16px; color: #333;">
        As a small thank you, we’ll gift you <strong>1 free month </strong> if you complete our quick review form 
      </p> 
      <p style="font-size: 16px; color: #333;">
      
      <div style="text-align: center; margin: 30px 0;">
        <a href="{feedback_form_url}" style="background-color: #0066cc; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-size: 16px;">Give Feedback</a>
      </div>

      <p style="font-size: 16px; color: #333;">Or if you'd like to support us publicly, you can also leave a short review here:</p>
     <p style="font-size: 16px; color: #333;">Get an <strong> extra free month </strong> if you submit with a picture of you!</p>   

      <div style="text-align: center; margin: 20px 0;">
        <a href="{review_form_url}" style="color: #0066cc; font-size: 15px;">Leave a Review</a>
      </div>

      <hr style="margin: 40px 0; border: none; border-top: 1px solid #ddd;">
      <p style="font-size: 12px; color: #999; text-align: center;">
        Sent with 💙 by SportsJobs Online  
        <br>If you have any questions, just reply this email</br>
      </p>
    </div>
  </body>
</div>"""


####

emails = ["francobetteo@gmail.com", "gene.mrq@gmail.com"]

# emails = [
#     "mayukhofficial12@gmail.com",
#     "bancheri.andreas@gmail.com",
#     "steeven7808@gmail.com",
#     "emmamnrainer@gmail.com",
#     "cspyksma@ucsb.edu",
#     "ghalydan@gmail.com",
#     "gonzalogarcia.c@icloud.com",
#     "tyler.ohl2135@gmail.com",
#     "felix.brust17@gmail.com",
#     "ekmcintosh@outlook.com",
#     "brandegilbert@gmail.com",
#     "kdgalsky@gmail.com",
#     "krao30120@gmail.com",
#     "maamar.izemrane@gmail.com",
#     "emre.yeloegrue@gmail.com",
#     "aaron593@mit.edu",
#     "jdcoop13@gmail.com",
#     "mattyice822@gmail.com",
#     "michael.larochelle7@gmail.com",
#     "seanchua873@gmail.com",
#     "theo.s.maisel@gmail.com",
#     "tzfelber77@gmail.com",
#     "s.shaheer.qadri@gmail.com",
#     "genie@fmscout.com",
#     "sebastian.tampu@gmail.com",
#     "plyanez2@illinois.edu",
#     "khtran133@gmail.com",
#     "apparao.prattipati@gmail.com"
# ]
success_emails = []

for email in emails:
    print(f"Sending email to {email}")

    try:
        r = resend.Emails.send(
            {
                "from": "Franco from SportsJobs Online <noreply@alerts.sportsjobs.online>",
                "to": email,
                "subject": "[sportsjobs] Enjoy an extra month on us 🎁",
                "reply_to": "franco@sportsjobs.online",
                "html": html_body,
            }
        )
        success_emails.append(email)
        print(f"Email sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")
