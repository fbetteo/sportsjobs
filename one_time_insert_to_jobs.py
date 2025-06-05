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
Position Overview:
This position will be an integral part of the Washington Commanders and will help refine the data environment to meet business needs, strategically problem solve, and achieve overall organizational objectives.

You will be working alongside members of the Business Intelligence department to help develop and maintain our business data warehouse. This includes managing connections to existing data sources, integrating new data sources, modeling current and historical data, and developing logic to ensure clean data. 
 
Responsibilities:

·       Collaborate with the Business Intelligence and ticket ops teams to clean and transform/model historical ticketing data from Ticketmaster to current SeatGeek language.

·       Develop and maintain ETL processes via API from various sources into our data warehouse.

·       Assist in the design of both data models and structures to support modeling and reporting processes.

·       Assist in the creation and maintenance of documentation – GitHub, in code, and about solution architecture.

·       Conduct thorough testing and seamless implementation of changes within the data warehouse environment.

·       Respond promptly and professionally to ad hoc requests from diverse departments within the organization.

 

Qualifications:

·       Bachelor's degree (in progress) in Computer Science, Engineering, Math, or related field

·       Strong knowledge of SQL, including Common Table Expressions (CTEs) and window functions.

·       Strong programming skills in Python or other scripting language used for data manipulation.

·       Understanding common practices and tools for building end-to-end data pipelines.

·       Problem-solving capabilities to discover, address and resolve issues

·       Exceptional communication skills with non-technical parties

·       Independent worker with close attention to detail 

·       Experience with data visualization tools such as Tableau or Power BI is a plus

·       Familiarity with Azure environment is a plus

·       Familiarity with Linux based servers is a plus

Salary: $15.00/hour

"""
full_description = md(description_raw, heading_style="ATX")


record = {
    "name": "Intern, Data Engineering",
    "status": "Open",
    "start_date": datetime.utcnow().date(),
    "url": "https://www.teamworkonline.com/football-jobs/washington-commanders-jobs/washington-commanders-jobs/intern-data-engineering-2123133",
    "location": "College Park, MD",
    "country": "united states",
    "country_code": "US",
    "seniority": "Internship",
    "description": full_description,
    "sport_list": "Football - NFL",
    "skills": ["SQL", "Python", "Tableau", "Power BI"],
    "job_area": "Data Engineer",
    "remote": False,
    "remote_office": "On-site",
    "salary": "15.00",
    "language": ["English"],
    "company": "Washington Commanders",
    "industry": "Sports",
    "job_type": "Temporary",
    "hours": "Fulltime",
    "logo_permanent_url": "https://cf-production.teamworkonline.com/uploads/public/thumb_b1afc48e-0215-4c8d-afea-b4239b5e22ab.jpg",
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
