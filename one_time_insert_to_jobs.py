## Use this conversation to paste the job description and get a structured record for the job posting.
# old from o3 (failed last time) https://chatgpt.com/c/6833c16d-cd28-8004-8216-f4ce7dfa60e4
# gpt5: https://chatgpt.com/c/68a477c4-bb38-8330-b613-83e6d3347c73


# Forward the DB connection from the hetzner server to your local machine
# ssh -L 5432:localhost:5432 root@188.245.110.228

# Steps
# - Replace the description_raw with the actual job description
# - Paste the record returned by chatGPT into the `record` variable
# - Update the URL to the job posting
# - Update the logo URL
# - Run everything


from datetime import datetime
from markdownify import markdownify as md

description_raw = """

Sport Science Internship – The Ohio State University Sport Science Program

Purpose
Embark on a journey at the intersection of sports, technology, and innovation. Contribute to the elite Ohio State Sport Science Team, with the opportunity to gain experience across all 36 sports.

Offers

Work with cutting-edge sport science technology including GPS, force plates, and much more.

Engage with athletes during data collection and interpretation.

Collaborate closely with professional staff from all parts of the sport performance team.

How to Apply
Email your resume, cover letter, and availability to the Sports Science Team at CENCERJR.1@OSU.EDU
.
"""
full_description = md(description_raw, heading_style="ATX")


record = {
    "name": "Sport Science Internship",
    "status": "Open",
    "start_date": datetime.utcnow().date().isoformat(),
    "url": "https://www.linkedin.com/posts/daniel-cencer-a72717121_were-looking-for-a-sport-science-intern-activity-7363547008596398081-oADy",
    "location": "Columbus, OH",
    "country": "united states",
    "country_code": "US",
    "seniority": "Internship",
    "description": full_description,
    "sport_list": "NULL",
    "skills": ["Sports Science", "Analytics", "Data", "Statistics"],
    "job_area": "Analytics",
    "remote": False,
    "remote_office": "Office",
    "salary": "",
    "language": ["English"],
    "company": "The Ohio State University Sport Science Program",
    "industry": "Sports",
    "job_type": "Temporary",
    "hours": "Fulltime",
    "logo_permanent_url": "https://media.licdn.com/dms/image/v2/C4E0BAQHM9OZD-HjNIA/company-logo_100_100/company-logo_100_100/0/1649856203275/the_ohio_state_university_department_of_athletics_logo?e=1758758400&v=beta&t=y-K4U7BsAADywMjZhL4CRjrOCfk3bqo_zZk8SVZuzGI",
    "post_duration": 30,
    "post_tier": "Free",
    "featured": "1 - regular",
    "creation_date": datetime.utcnow().isoformat(),
}


from hetzner_utils import (
    start_postgres_connection,
    get_recent_urls,
    get_skills,
    insert_records,
)


conn = start_postgres_connection()
with conn as conn:
    insert_records(conn, "jobs", record)
