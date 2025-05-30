import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag
from utils import add_industry, add_job_area, add_sport_list, search_for_png_image
from hetzner_utils import (
    start_postgres_connection,
    get_recent_urls,
    insert_records,
    get_skills,
)
from utils import is_remote_global, add_job_area, search_for_png_image, find_country
import utils
import markdownify

conn = start_postgres_connection()
try:
    with conn as conn:
        recent_urls = get_recent_urls(conn)
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d")
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
            "Engineering",
            "MLOps",
            "ETL",
            "DBT",
            "Sports Analytics",
            "Data Visualization",
            "A/B testing",
            "Tableau",
            "Power BI",
            "AI",
        ]

        skills = skills + skills_to_search

        companies = {
            "sumersports": {
                "board_name": "sumersports",
                "logo": [
                    {
                        "url": "",
                        "filename": "sumersports.png",
                    }
                ],
            },
            "teamworks": {
                "board_name": "teamworks-careers",
                "logo": [
                    {
                        "url": "",
                        "filename": "teamworks-careers.png",
                    }
                ],
            },
            "boston_legacy_fc": {
                "board_name": "nwsl-boston-open-positions",
                "logo": [
                    {
                        "url": "",
                        "filename": "boston_legacy_fc.png",
                    }
                ],
            },
        }

        def html_to_markdown(element):
            if isinstance(element, NavigableString):
                return str(element).strip() + " "
            elif isinstance(element, Tag):
                if element.name == "ul":
                    return (
                        "\n".join(
                            [
                                f"* {html_to_markdown(item)}"
                                for item in element.find_all("li")
                            ]
                        )
                        + "\n"
                    )
                elif element.name == "ol":
                    return "\n".join(
                        [
                            f"1. {html_to_markdown(item)}"
                            for item in element.find_all("li")
                        ]
                    )
                else:
                    # Recursively process other tags
                    return "".join(
                        html_to_markdown(child) for child in element.children
                    ).strip()
            return ""

        for company, attrs in companies.items():
            url = f"https://api.rippling.com/platform/api/ats/v2/board/{attrs['board_name']}/jobs"
            headers = {"Accept": "application/json"}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"Error in request for {company}: {response.status_code}")
                continue

            data = response.json()
            for job in data.get("items", []):
                job_url = job.get("url")
                if job_url in recent_urls:
                    continue

                title = job.get("name", "")

                job_role_response = requests.get(
                    f'{url}/{job.get("id")}', headers=headers
                )
                if response.status_code != 200:
                    print(
                        f"Error in request for job role in {company}: {response.status_code}"
                    )
                    continue
                job_role_data = job_role_response.json()
                description = job_role_data.get("description", {}).get(
                    "role", ""
                )  # no description in API
                full_description = markdownify.markdownify(
                    description, heading_style="ATX"
                )

                # Just techinical skills we want to filter by
                pattern = r"\b(?:" + "|".join(skills_to_search) + r")\b"
                skills_required = [
                    skill.lower()
                    for skill in set(
                        re.findall(
                            pattern,
                            full_description + " " + job["name"],
                            re.IGNORECASE,
                        )
                    )
                ]
                skills_required_format = [
                    skill for skill in skills if skill.lower() in skills_required
                ]

                none_skill = len(skills_required) < 2

                if (job_url in recent_urls) or (none_skill):
                    continue

                # Duplicate but to add all skills. I should create a function to avoid duplicating.
                pattern = r"\b(?:" + "|".join(skills) + r")\b"
                skills_required = [
                    skill.lower()
                    for skill in set(
                        re.findall(
                            pattern,
                            full_description + " " + job["name"],
                            re.IGNORECASE,
                        )
                    )
                ]
                skills_required_format = [
                    skill for skill in skills if skill.lower() in skills_required
                ]

                title = job["name"]
                createdAt = job_role_data["createdOn"]
                location = job["locations"][0]["name"]
                workplaceType = job["locations"][0]["workplaceType"]

                try:
                    country = find_country(location)["country"]
                    country_code = find_country(location)["country_code"]
                except:
                    country = "united states"
                    country_code = "US"

                if (
                    ("remote" in location.lower())
                    | ("remote" in title.lower())
                    | ("remote" in full_description.lower())
                    | ("remote" in workplaceType.lower())
                    # workplaceType is a string
                ):
                    accepts_remote = "Yes"
                else:
                    accepts_remote = "No"
                # workplaceType = job["workplaceType"]
                # if workplaceType.upper() == "REMOTE":
                #     accepts_remote = "Yes"
                # else:
                #     accepts_remote = "No"
                remote_office = is_remote_global(full_description)

                job_area = add_job_area(skills_required_format)

                if re.search(
                    r"\b(?:intern|internship|internships)\b",
                    title,
                    re.IGNORECASE,
                ):
                    seniority = "Internship"
                elif re.search(r"\b(?:junior)\b", title, re.IGNORECASE):
                    seniority = "Junior"
                else:
                    seniority = "With Experience"

                # hours = job["categories"].get("commitment", "Fulltime")
                hours = "Fulltime"

                if re.search(
                    r"\b(?:part time|parttime)\b",
                    title + " " + description,
                    re.IGNORECASE,
                ):
                    hours = "Part time"

                if hours in [
                    "Full-time",
                ]:
                    hours = "Fulltime"

                if hours in ["Part-time", "Parttime"]:
                    hours = "Part time"

                if hours != "Part time" and hours != "Fulltime":
                    hours = "Fulltime"

                # Industry
                industry = []
                if re.search(
                    r"\b(?:sports betting|betting|gambling)\b",
                    title + " " + description,
                    re.IGNORECASE,
                ):
                    industry += ["Betting"]
                elif re.search(
                    r"\b(?:esports|esport)\b", title + " " + description, re.IGNORECASE
                ):
                    industry += ["Esports"]
                else:
                    industry += ["Sports"]

                # Sport
                sport_list = []
                if re.search(
                    r"\b(?:basketball|nba)\b",
                    title + " " + description,
                    re.IGNORECASE,
                ):
                    sport_list += ["Basketball"]
                elif re.search(
                    r"\b(?:football|NFL)\b", title + " " + description, re.IGNORECASE
                ):
                    sport_list += ["Football - NFL"]
                elif re.search(
                    r"\b(?:football|soccer|MLS)\b",
                    title + " " + description,
                    re.IGNORECASE,
                ):
                    sport_list += ["Football - Soccer"]
                elif re.search(
                    r"\b(?:baseball|MLB)\b", title + " " + description, re.IGNORECASE
                ):
                    sport_list += ["Baseball"]
                elif re.search(
                    r"\b(?:hockey|NHL)\b", title + " " + description, re.IGNORECASE
                ):
                    sport_list += ["Hockey"]
                elif re.search(
                    r"\b(?:golf|PGA)\b", title + " " + description, re.IGNORECASE
                ):
                    sport_list += ["Golf"]
                elif re.search(
                    r"\b(?:tennis|ATP)\b", title + " " + description, re.IGNORECASE
                ):
                    sport_list += ["Tennis"]
                elif re.search(
                    r"\b(?:rugby|NRL)\b", title + " " + description, re.IGNORECASE
                ):
                    sport_list += ["Rugby"]
                elif re.search(
                    r"\b(?:mma|ufc)\b", title + " " + description, re.IGNORECASE
                ):
                    sport_list += ["MMA"]
                elif re.search(
                    r"\b(?:boxing)\b", title + " " + description, re.IGNORECASE
                ):
                    sport_list += ["Boxing"]

                logo = attrs.get("logo", [])

                if job_role_data.get("board", {}).get("logo", {}).get("url", ""):
                    logo[0]["url"] = (
                        job_role_data.get("board", {}).get("logo", {}).get("url", "")
                    )

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

                salary_data = []
                if len(salary_data) > 0:
                    salary = salary_data[0].get("max_cents", None)
                    try:
                        salary = int(salary) / 100
                    except:
                        salary = ""
                else:
                    salary = ""

                if not salary:
                    try:
                        salary = utils.extract_salary(full_description)[0]
                    except:
                        salary = ""

                record = {
                    "name": title,
                    "status": "Open",
                    "start_date": current_time,
                    "url": job_url,
                    "location": location,
                    "country": country,
                    "country_code": country_code,
                    "seniority": seniority,
                    "description": full_description,
                    "sport_list": sport_list[0] if sport_list else None,
                    "skills": skills_required_format,
                    "job_area": job_area,
                    "remote": accepts_remote,
                    "remote_office": remote_office,
                    "salary": str(salary),
                    "language": [job.get("language", "")],
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
except Exception as e:
    print(f"Error: {e}")
