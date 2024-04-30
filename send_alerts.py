import resend
import os

from pyairtable import Api
import time
import json

import pandas as pd
import numpy as np

# from dotenv import load_dotenv, find_dotenv

os.getcwd()

# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/sportsjobs/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_ALERTS_TABLE = os.getenv("AIRTABLE_ALERTS_TABLE")
AIRTABLE_USERS_TABLE = os.getenv("AIRTABLE_USERS_TABLE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")

resend.api_key = os.environ["RESEND_API_KEY"]

api = Api(AIRTABLE_TOKEN)


alerts_table = api.table(AIRTABLE_BASE, AIRTABLE_ALERTS_TABLE).all()
users_table = api.table(AIRTABLE_BASE, AIRTABLE_USERS_TABLE).all()
jobs_table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE).all()


fields_data = [item["fields"] for item in jobs_table]

from datetime import datetime, timedelta

# Get today's date
today = datetime.now()

# Calculate the date 7 days ago
seven_days_ago = today - timedelta(days=7)
yesterday = today - timedelta(days=1)


jobs_data = pd.DataFrame(fields_data)
jobs_data = jobs_data.query("@pd.to_datetime(`Start date`) >= @seven_days_ago ")
jobs_data["sport_list"] = jobs_data["sport_list"].apply(
    lambda x: ["Any"] if pd.isna(x) else x
)
jobs_data["skills"] = jobs_data["skills"].apply(lambda x: ["Any"] if x is np.nan else x)
jobs_data_yesterday = jobs_data.query("@pd.to_datetime(`Start date`) >= @yesterday ")


def get_users_with_alerts(alerts_table):
    new_records = []
    keys_to_extract = ["Name", "email"]
    for record in alerts_table:
        filtered_dict = {
            k: record["fields"][k] for k in keys_to_extract if k in record["fields"]
        }
        new_records.append(filtered_dict)
    return new_records


def get_plan_per_user(users_table):
    new_records = []
    keys_to_extract = ["email", "plan"]
    for record in users_table:
        filtered_dict = {
            k: record["fields"][k] for k in keys_to_extract if k in record["fields"]
        }
        new_records.append(filtered_dict)
    return new_records


user_alerts_df = pd.DataFrame(get_users_with_alerts(alerts_table))
plan_user_df = pd.DataFrame(get_plan_per_user(users_table))

# Merge the two DataFrames
merged_df = pd.merge(user_alerts_df, plan_user_df, on="email", how="left")
merged_df["frequency"] = np.where(
    merged_df["plan"].isin(
        [
            "lifetime",
            "yearly_subscription",
            "monthly_subscription",
            "weekly_subscription",
        ]
    ),
    "daily",
    "weekly",
)

PROTECTED_LIST = ["francobetteo@gmail.com", "gene.mrq@gmail.com"]
merged_df = merged_df.loc[~merged_df["email"].isin(PROTECTED_LIST), :]


def create_filter(jobs_data, alert):
    jobs_data_len = jobs_data.shape[0]
    country_mask = [True] * jobs_data_len
    seniority_mask = [True] * jobs_data_len
    sport_mask = [True] * jobs_data_len
    skills_mask = [True] * jobs_data_len
    remote_office_mask = [True] * jobs_data_len
    industry_mask = [True] * jobs_data_len
    hours_mask = [True] * jobs_data_len

    if "country" in alert:
        # like this because is single option in jobs
        country_mask = jobs_data["country"].isin(alert["country"])
    if "seniority" in alert:
        # like this because is single option in jobs
        seniority_mask = jobs_data["seniority"].isin(alert["seniority"])
    if "sport_list" in alert:
        sport_mask = jobs_data["sport_list"].apply(
            lambda x: (
                len(set(x) & (set(alert["sport_list"]))) > 0 if x is not None else False
            )
        )
    if "skills" in alert:
        skills_mask = jobs_data["skills"].apply(
            lambda x: (
                len(set(x) & (set(alert["skills"]))) > 0 if x is not None else False
            )
        )
    if "remote_office" in alert:
        remote_office_mask = jobs_data["remote_office"].isin(alert["remote_office"])
    if "industry" in alert:
        industry_mask = jobs_data["industry"].apply(
            lambda x: (
                len(set(x) & (set(alert["industry"]))) > 0 if x is not None else False
            )
        )
    if "hours" in alert:
        hours_mask = jobs_data["hours"].apply(
            lambda x: (
                len(set(x) & (set(alert["hours"]))) > 0 if x is not None else False
            )
        )

    return (
        np.array(country_mask)
        & np.array(seniority_mask)
        & np.array(sport_mask)
        & np.array(skills_mask)
        & np.array(remote_office_mask)
        & np.array(industry_mask)
        & np.array(hours_mask)
    )


# aa = create_filter(jobs_data, alerts_table[1]["fields"])


def get_jobs_per_alert(alerts_table, days_before):
    new_records = []
    keys_to_extract = ["email", "alert", "frequency"]
    for record in alerts_table:
        filtered_dict = {
            k: record["fields"][k] for k in keys_to_extract if k in record["fields"]
        }
        new_records.append(filtered_dict)
    return new_records


alerts_table_to_deplete = alerts_table.copy()
alerts_table_to_deplete

# to debug
alerts_table_to_deplete.append(
    {
        "id": "reco5mk7LHiDE3juS",
        "createdTime": "2024-04-13T17:39:00.000Z",
        "fields": {
            "skills": ["Sports"],
            "Name": "example",
            "email": "francobetteo@gmail.com",
        },
    }
)

for premium_member in merged_df.loc[merged_df["frequency"] == "daily"].iterrows():
    alerts_used = []
    for i, alert in enumerate(alerts_table_to_deplete):
        if alert["fields"]["email"] == premium_member[1]["email"]:
            print(alert["fields"]["email"])
            alerts_used.append(i)
            try:
                job_filter = create_filter(jobs_data_yesterday, alert["fields"])
            except:
                continue
            jobs_to_send = jobs_data_yesterday[job_filter]
            if jobs_to_send.shape[0] == 0 or jobs_to_send is None:
                continue
            html_body = f"""
            <head>
            
        </head>

            <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; text-align: center; color: #333;">
    <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
        <h1 style="color: #0066cc;">Sportsjobs Online</h1>
        <h2 style="color: #0066cc;">Hi {alert['fields']['Name']}</h2>
        <h2 style="color: #0066cc;">These are the jobs we found for you</h2>
                """
            for job in jobs_to_send.iterrows():
                html_body += f"""
                <table style="margin: 20px auto; border-collapse: collapse; width: 100%;">
            <tbody>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: left;"><img src="{job[1]['logo_permanent_url']}" alt="Logo" width="75" style="vertical-align: middle;"></td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: left;"><a href="{job[1]['job_detail_url']}?utm_source=alerts" target="_blank" style="color: #0066cc; text-decoration: none;">{job[1]['Name']}</a></td>
                </tr>
            </tbody>
        </table>
        """

            r = resend.Emails.send(
                {
                    "from": "noreply@alerts.sportsjobs.online",
                    "to": alert["fields"]["email"],
                    "subject": "Sports Jobs of the day! - Check out the new jobs available",
                    "html": html_body,
                }
            )

        alerts_table_to_deplete = [
            i for j, i in enumerate(alerts_table_to_deplete) if j not in alerts_used
        ]

        # To avoid bugs sending to other people
        job_filter = None


# PREMIUM
# loopear por los usuarios daily
# traer las alertas correspondiente
# loopear por ellas (si tiene mas de una alerta)
# traer los jobs del ultimo dia que cumplan los requisitos
# enviar el email


# FREE
# loopear por los usuarios weekly
# traer las alertas correspondiente
# loopear por ellas (si tiene mas de una alerta)
# traer los jobs de los ultimos 7 dias que cumplan los requisitos
# enviar el email
from datetime import datetime

# Get today's date
today = datetime.now()

# Get the weekday name
weekday_name = today.strftime("%A")

if weekday_name == "Wednesday":

    alerts_used = []
    for free_member in merged_df.loc[merged_df["frequency"] == "weekly"].iterrows():
        for i, alert in enumerate(alerts_table_to_deplete):
            if alert["fields"]["email"] == free_member[1]["email"]:
                print(alert["fields"]["email"])
                alerts_used.append(alert["id"])
                try:
                    job_filter = create_filter(jobs_data, alert["fields"])
                except:
                    continue
                jobs_to_send = jobs_data[job_filter]
                if jobs_to_send.shape[0] == 0 or jobs_to_send is None:
                    continue
                html_body = f"""
                <head>
                
            </head>

                <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; text-align: center; color: #333;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
            <h1 style="color: #0066cc;">Sportsjobs Online</h1>
            <h2 style="color: #0066cc;">Hi {alert['fields']['Name']}</h2>
            <h2 style="color: #0066cc;">These are the jobs we found for you this week</h2>
            <h4 style="color: #3d1f89;">Become premium to get daily alerts and apply right on time!</h4>
                    """
                for job in jobs_to_send.iterrows():
                    html_body += f"""
                    <table style="margin: 20px auto; border-collapse: collapse; width: 100%;">
                <tbody>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: left;"><img src="{job[1]['logo_permanent_url']}" alt="Logo" width="75" style="vertical-align: middle;"></td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: left;"><a href="{job[1]['job_detail_url']}?utm_source=alerts" target="_blank" style="color: #0066cc; text-decoration: none;">{job[1]['Name']}</a></td>
                    </tr>
                </tbody>
            </table>
            """
                html_body += f"""
                        <h2><a href="https://www.sportsjobs.online/member-plan?utm_source=alerts" target="_blank" style="color: #0066cc; text-decoration: none;">Becoming a Premium Member</a></h2>
            <ol style="text-align: left; display: inline-block; text-align: left;">
                <li style="margin-bottom: 10px;">🔔 Premium members receive daily alerts instead of weekly. <strong>Apply before all your competition.</strong></li>
                <li style="margin-bottom: 10px;">🔎 By becoming a premium member you get <strong>access to all the jobs anytime.</strong></li>
                <li style="margin-bottom: 10px;">💹 You <strong>increase your chances of landing your dream job.</strong> This means looking for your job in one place and not opening 10 tabs every time, which is a waste of time and boring.</li>
                <li style="margin-bottom: 10px;">⏳ You get <strong>priority</strong> in support and feature request.</li>
                <li style="margin-bottom: 10px;">🏋️ You support me in this adventure -> I can add more jobs increasing the size of the database and use more time to find useful content.</li>
            </ol>
            
            <a href="https://www.sportsjobs.online/member-plan?utm_source=alerts" target="_blank" style="display: inline-block; background-color: #0066cc; color: #fff; padding: 10px 20px; border-radius: 5px; font-size: 19px; text-decoration: none;">Become Premium!</a>
        </div>"""

                r = resend.Emails.send(
                    {
                        "from": "noreply@alerts.sportsjobs.online",
                        "to": alert["fields"]["email"],
                        "subject": "Sports Jobs of the day! - Check out the new jobs available",
                        "html": html_body,
                    }
                )

            alerts_table_to_deplete = [
                i for i in alerts_table_to_deplete if i["id"] not in alerts_used
            ]

            # To avoid bugs sending to other people
            job_filter = None


######################
