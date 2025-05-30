## Use this conversation to paste the job description and get a structured record for the job posting.
# https://chatgpt.com/c/6833c16d-cd28-8004-8216-f4ce7dfa60e4

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
Backend Data Engineer
Denver
The Denver Broncos are one of the most popular franchises in all of sports. Whether judged by the measure of wins and championships, attendance, national television exposure or by the Broncos' reputation locally and throughout the NFL, there are few parallels in the world of professional sports. We are dedicated to being the best team to cheer for, play for, and work for across all of sports. We are looking for employees who are passionate about what they do, have fun doing it, and proud to represent the Denver Broncos Football Club and Empower Field at Mile High.

Job Summary: The Denver Broncos Football Technology and Research Department is looking for a hard-working and talented Backend Data Engineer to join our software engineering team. The Backend Data Engineer will be responsible for building and maintaining the systems and infrastructure that enable data collection, transformation, storage, and access across the Football Operations departments. This role involves working with complex data pipelines, optimizing data flow, and ensuring the reliability, accuracy and security of datasets. You will work closely with data scientists, analysts, and software engineers in support of our internal applications, ensuring that data pipelines are reliable, scalable, and secure. The ideal candidate will collaborate with team members to drive projects from design to deployment.

 

Key Responsibilities

· Develop, optimize, and maintain ETL pipelines for efficient data processing.

· Design and implement data models, storage solutions, and retrieval mechanisms.

· Perform data extraction, transformation, and loading from various structured and unstructured sources.

· Ensure data integrity, accuracy, and security through effective governance policies and unit testing.

· Develop and maintain data infrastructure on-premise and in cloud-based environments such as AWS, Azure, or Google Cloud.

· Automate data pipeline deployment, monitoring, and optimization using DevOps tools.

· Troubleshoot data-related issues and implement solutions for performance improvement.

· Develop and maintain RESTful APIs for data access and integration with our front-end applications.

· Work with our research team to support data analysis, visualization, and reporting.

· Create and maintain documentation of data engineering processes, tools, workflows and API endpoints.

 

 

Minimum Requirements

· Bachelor’s degree in Computer Science, Information Systems or a related field (or equivalent work experience) with a strong technical background

· 5+ years of professional experience in data engineering, software engineering or related role.

 

 

Preferred Skills and Ability

· Experience with workflow orchestration tools (Airflow, Conductor, Azure Data Factory, etc.)

· Experience with cloud based big data platforms (Data Bricks, Google Big Data, etc.)

· Proficient in using Python or R for data transformation.

· Experience with C# and Entity Framework

· Proficiency in SQL and database management systems (SQL Server, PostgreSQL) with knowledge of NoSQL systems.

· Familiarity with DevOps tools such as Docker, Kubernetes, and CI/CD pipelines.

· Familiarity with machine learning/MLOps workflows

· Ability to develop, optimize and maintain APIs on multiple platforms.

· Able to own and drive individual projects as well as work on a high performing team in a fast-paced environment.

· Detail oriented with strong analytical skills and a willingness to learn and implement new technologies, must have a growth mindset.

· Strong interpersonal and relationship management skills.

· The ability to work long and flexible hours, including evenings, weekends and holidays.

· Strong knowledge of football is a plus

Note: This document describes typical duties and responsibilities and is not intended to limited management from assigning other work as required or desired.

 

In accordance with the Colorado Equal Pay for Equal Work Act, the salary for this role is $124,700 - $141,200. This position may require you to work flexible hours including weekends, evenings and holidays outside of a normal working hour as needed.
"""
full_description = md(description_raw, heading_style="ATX")


record = {
    "name": "Backend Data Engineer",
    "status": "Open",
    "start_date": datetime.utcnow().date(),
    "url": "https://job-boards.greenhouse.io/denverbroncosteamllc/jobs/4742698008",
    "location": "Denver, CO",
    "country": "united states",
    "country_code": "US",
    "seniority": "With Experience",
    "description": full_description,
    "sport_list": "Football - NFL",
    "skills": [
        "Python",
        "SQL",
        "Airflow",
        "Azure",
        "Databricks",
        "AWS",
        "Postgres",
        "NoSQL",
        "Docker",
        "Kubernetes",
        "Devops",
        "R",
        "Data Engineering",
        "MLOps",
    ],
    "job_area": "Data Engineer",
    "remote": False,
    "remote_office": "On-site",
    "salary": "124700-141200",
    "language": ["English"],
    "company": "Denver Broncos",
    "industry": "Sports",
    "job_type": "Permanent",
    "hours": "Fulltime",
    "logo_permanent_url": "https://s8-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/132/200/original/logo-lockup-db-smc.png?1717454743",
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
