### Personio

import requests
import xml.etree.ElementTree as ET
import html
import re
import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

from utils import is_remote_global, add_job_area, search_for_png_image, find_country
import utils
from hetzner_utils import (
    start_postgres_connection,
    get_recent_urls,
    get_skills,
    insert_records,
)

os.getcwd()

# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/redditbot/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")

conn = start_postgres_connection()

try:
    with conn as conn:
        recent_urls = get_recent_urls(conn)
        skills = get_skills(conn)

        skills_to_search = [
            "Devops",
            "Machine Learning",
            "Data Science",
            "Data Scientist",
            "Data Analytics",
            "Business Intelligence",
            "Bayesian",
            "Data Engineering",
            "Data Engineer",
            "MLOps",
            "ETL",
            "DBT",
            "Sports Analytics",
            "Data Visualization",
            "A/B testing",
            "Tableau",
            "Power BI",
            "AI",
            "Full Stack",
            "Software Engineer",
            "Python",
            "JavaScript",
            "React",
            "API",
            "Business Development",
        ]

        skills = skills + skills_to_search

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d")

        def clean_html_content(html_content):
            """Clean HTML content and convert to plain text"""
            # Remove CDATA sections
            html_content = html_content.replace("<![CDATA[", "").replace("]]>", "")
            # Unescape HTML entities
            html_content = html.unescape(html_content)
            # Simple HTML tag removal (for basic formatting)
            html_content = re.sub(r"<br\s*/?>", "\n", html_content)
            html_content = re.sub(r"<li>", "• ", html_content)
            html_content = re.sub(r"</li>", "\n", html_content)
            html_content = re.sub(r"<ul>", "\n", html_content)
            html_content = re.sub(r"</ul>", "\n", html_content)
            html_content = re.sub(r"<[^>]+>", "", html_content)
            return html_content.strip()

        def extract_job_descriptions(job_descriptions):
            """Extract and format job descriptions from XML"""
            full_description = ""
            for job_desc in job_descriptions:
                name = job_desc.find("name")
                value = job_desc.find("value")

                if name is not None and value is not None:
                    section_name = name.text if name.text else ""
                    section_content = clean_html_content(
                        value.text if value.text else ""
                    )

                    if section_name and section_content:
                        full_description += (
                            f"## {section_name}\n\n{section_content}\n\n"
                        )

            return full_description.strip()

        companies = {
            "PACETEQ": {
                "personio_name": "paceteq-gmbh",
                "logo": [
                    {
                        "url": "https://images.crunchbase.com/image/upload/c_pad,h_256,w_256,f_auto,q_auto:eco,dpr_1/ekectgvnwezgxewyrhjc",
                        "filename": "paceteq.png",
                    }
                ],
            },
        }

        for company, attributes in companies.items():
            xml_url = f"http://{attributes['personio_name']}.jobs.personio.com/xml"

            try:
                response = requests.get(xml_url)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Error fetching XML for {company}: {e}")
                continue

            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as e:
                print(f"Error parsing XML for {company}: {e}")
                continue

            for position in root.findall("position"):
                # Extract basic job information
                job_id = position.find("id")
                title = position.find("name")
                office = position.find("office")
                department = position.find("department")
                employment_type = position.find("employmentType")
                seniority = position.find("seniority")
                schedule = position.find("schedule")
                keywords = position.find("keywords")
                created_at = position.find("createdAt")

                # Extract job descriptions
                job_descriptions = position.find("jobDescriptions")

                if job_id is None or title is None:
                    continue

                job_id_text = job_id.text if job_id.text else ""
                title_text = title.text if title.text else ""
                office_text = office.text if office.text else ""
                department_text = department.text if department.text else ""
                employment_type_text = (
                    employment_type.text if employment_type.text else "permanent"
                )
                seniority_text = seniority.text if seniority.text else "experienced"
                schedule_text = schedule.text if schedule.text else "full-time"
                keywords_text = keywords.text if keywords.text else ""
                created_at_text = created_at.text if created_at.text else ""

                # Build job URL
                url = f"https://{attributes['personio_name']}.jobs.personio.com/job/{job_id_text}"

                # Skip if URL already exists
                if url in recent_urls:
                    continue

                # Extract and format full description
                full_description = ""
                if job_descriptions is not None:
                    job_desc_elements = job_descriptions.findall("jobDescription")
                    full_description = extract_job_descriptions(job_desc_elements)

                # Combine all text for skill matching
                all_text = f"{title_text} {full_description} {keywords_text}"

                # Technical skills filtering
                pattern = r"\b(?:" + "|".join(skills_to_search) + r")\b"
                skills_required = [
                    set(skill.lower())
                    for skill in set(re.findall(pattern, all_text, re.IGNORECASE))
                ]
                skills_required_format = [
                    skill for skill in skills if skill.lower() in skills_required
                ]

                # Skip if no relevant technical skills found
                none_skill = len(skills_required) < 2
                if none_skill:
                    continue

                # Extract all matching skills (not just technical)
                pattern = r"\b(?:" + "|".join(skills) + r")\b"
                skills_required = [
                    skill.lower()
                    for skill in set(re.findall(pattern, all_text, re.IGNORECASE))
                ]
                skills_required_format = [
                    skill for skill in skills if skill.lower() in skills_required
                ]

                # Determine location and country
                location = office_text
                try:
                    country_info = find_country(location)
                    country = country_info["country"]
                    country_code = country_info["country_code"]
                except:
                    country = "united states"
                    country_code = "US"
                # Hardcoded for Personio Germany
                if "- GER" in location:
                    country = "germany"
                    country_code = "DE"

                # Determine remote work
                if (
                    ("remote" in location.lower())
                    | ("remote" in title_text.lower())
                    | ("remote" in full_description.lower())
                    | ("hybrid" in location.lower())
                    | ("hybrid" in title_text.lower())
                    | ("hybrid" in full_description.lower())
                ):
                    accepts_remote = "Yes"
                else:
                    accepts_remote = "No"

                remote_office = is_remote_global(full_description)
                job_area = add_job_area(skills_required_format)

                # Determine seniority level
                if re.search(
                    r"\b(?:intern|internship|internships)\b", title_text, re.IGNORECASE
                ):
                    seniority_level = "Internship"
                elif re.search(
                    r"\b(?:junior|entry-level)\b",
                    title_text + " " + seniority_text,
                    re.IGNORECASE,
                ):
                    seniority_level = "Junior"
                else:
                    seniority_level = "With Experience"

                # Determine hours
                hours = "Fulltime"
                if re.search(
                    r"\b(?:part time|parttime|part-time)\b",
                    title_text + " " + schedule_text,
                    re.IGNORECASE,
                ):
                    hours = "Part time"

                # Determine industry
                industry = []
                if re.search(
                    r"\b(?:sports betting|betting|gambling)\b", all_text, re.IGNORECASE
                ):
                    industry += ["Betting"]
                elif re.search(r"\b(?:esports|esport)\b", all_text, re.IGNORECASE):
                    industry += ["Esports"]
                else:
                    industry += ["Sports"]

                # Determine sport
                sport_list = []
                if re.search(r"\b(?:basketball|nba)\b", all_text, re.IGNORECASE):
                    sport_list += ["Basketball"]
                elif re.search(r"\b(?:football|NFL)\b", all_text, re.IGNORECASE):
                    sport_list += ["Football - NFL"]
                elif re.search(r"\b(?:football|soccer|MLS)\b", all_text, re.IGNORECASE):
                    sport_list += ["Football - Soccer"]
                elif re.search(r"\b(?:baseball|MLB)\b", all_text, re.IGNORECASE):
                    sport_list += ["Baseball"]
                elif re.search(r"\b(?:hockey|NHL)\b", all_text, re.IGNORECASE):
                    sport_list += ["Hockey"]
                elif re.search(r"\b(?:golf|PGA)\b", all_text, re.IGNORECASE):
                    sport_list += ["Golf"]
                elif re.search(r"\b(?:tennis|ATP)\b", all_text, re.IGNORECASE):
                    sport_list += ["Tennis"]
                elif re.search(r"\b(?:rugby|NRL)\b", all_text, re.IGNORECASE):
                    sport_list += ["Rugby"]
                elif re.search(r"\b(?:mma|ufc)\b", all_text, re.IGNORECASE):
                    sport_list += ["MMA"]
                elif re.search(r"\b(?:boxing)\b", all_text, re.IGNORECASE):
                    sport_list += ["Boxing"]
                elif re.search(
                    r"\b(?:motorsport|racing|formula|f1)\b", all_text, re.IGNORECASE
                ):
                    sport_list += ["Motorsport"]

                # Get logo
                logo = attributes.get("logo", [])
                if len(logo) == 0:
                    google_logo = search_for_png_image(company)
                    if google_logo:
                        logo = google_logo
                    else:
                        logo = []

                if len(logo) > 0:
                    logo_permanent_url = logo[0]["url"]
                else:
                    logo_permanent_url = ""

                # Extract salary (if available)
                salary = ""
                try:
                    salary = utils.extract_salary(full_description)[0]
                except:
                    salary = ""

                # Create record for database
                record = {
                    "name": title_text,
                    "status": "Open",
                    "start_date": current_time,
                    "url": url,
                    "location": location,
                    "country": country,
                    "country_code": country_code,
                    "seniority": seniority_level,
                    "description": full_description,
                    "sport_list": sport_list[0] if sport_list else None,
                    "skills": skills_required_format,
                    "job_area": job_area,
                    "remote": accepts_remote,
                    "remote_office": remote_office,
                    "salary": str(salary),
                    "language": ["English"],
                    "company": company,
                    "industry": industry[0] if industry else None,
                    "job_type": "Permanent",
                    "hours": hours,
                    "logo_permanent_url": logo_permanent_url,
                    "post_duration": 30,
                    "post_tier": "Free",
                    "featured": "1 - regular",
                    "creation_date": now,
                }

                insert_records(conn, "jobs", record)
                print(f"Inserted job: {title_text} at {company}")

except Exception as e:
    print(f"Error occurred: {e}")
finally:
    # Ensure the connection is closed if still open
    if conn and conn.closed == 0:
        conn.close()
        print("Connection closed.")
