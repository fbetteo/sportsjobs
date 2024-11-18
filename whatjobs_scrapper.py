import requests
from bs4 import BeautifulSoup


import os
from pyairtable import Api
import requests
import requests.auth
import re
import time
from dotenv import load_dotenv, find_dotenv
import markdownify
from utils import is_remote_global, add_job_area, search_for_png_image, extract_salary
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

api = Api(AIRTABLE_TOKEN)
table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)
conn = start_postgres_connection()
from datetime import datetime

# URLS POSTED IN THE LAST MONTH
all = table.all(formula="{days_since_uploaded} < 30")
recent_urls = [record["fields"]["url"] for record in all]

try:
    with conn as conn:
        recent_urls = get_recent_urls(conn)

        # LIST OF SKILLS AVAILABLE IN AIRTABLE
        # skills_column = [field for field in table.schema().fields if field.name == "skills"]
        # skills = [skill.name for skill in skills_column[0].options.choices]

        skills = get_skills(conn)

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d")

        # find which companies post on lever
        # loop and extract postings related to Sports
        # post them if they are not on airtable
        # if they are on airtable, update the last updated date MAYBE
        from urllib.request import urlopen
        import re as r

        def getIP():
            d = str(urlopen("http://checkip.dyndns.com/").read())

            return r.compile(r"Address: (\d+\.\d+\.\d+\.\d+)").search(d).group(1)

        max_trials = 5
        trial = 0
        while trial < max_trials:
            try:
                IP = getIP()
                break
            except Exception as e:
                print(f"Attempt {trial+1} failed. Retrying...")
                trial += 1
                time.sleep(2)  # wait for 2 seconds before retrying
                if trial == max_trials:
                    print(
                        f"Failed to get IP after {max_trials} attempts. Ending script."
                    )
                    exit(1)

        for country_id in [5039, 5040, 5041, 5042, 5043, 5044]:
            print(country_id)

            country_map = {
                5039: ["united states", "US"],
                5040: ["united kingdom", "GB"],
                5041: ["germany", "DE"],
                5042: ["australia", "AU"],
                5043: ["canada", "CA"],
                5044: ["india", "IN"],
            }

            parameters = {
                "publisher": country_id,
                "user_ip": IP,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "keyword": "sports analytics",
                "limit": 50,
            }

            # Set URL
            # url = '/api/jobs.xml?%s' % urllib.urlencode(parameters)

            # Exec and return the result
            response = requests.get(
                "https://api.whatjobs.com/api/v1/jobs.json", params=parameters
            )

            if response.status_code != 200:
                print("Error in request")
                continue

            for job in response.json().get("data", []):

                description = job["snippet"]
                # list_text = description.replace("<li>", "* ").replace("</li>", "  \n")

                # soup = BeautifulSoup(list_text, "html.parser")
                # soup_parsed = soup.get_text()
                full_description = markdownify.markdownify(
                    description, heading_style="ATX"
                )

                pattern = r"\b(?:" + "|".join(skills) + r")\b"
                skills_required = [
                    skill.lower()
                    for skill in set(
                        re.findall(
                            pattern,
                            full_description + " " + job["title"],
                            re.IGNORECASE,
                        )
                    )
                ]
                skills_required_format = [
                    skill for skill in skills if skill.lower() in skills_required
                ]

                none_skill = len(skills_required) == 0

                if (
                    (job["url"] in recent_urls)
                    or (none_skill)
                    or (job["age_days"] > 40)
                ):
                    continue

                title = job["title"]
                createdAt = job["age"]
                url = job["url"]
                location = job["location"]
                country = country_map[country_id][0]
                country_code = country_map[country_id][1]
                # I don't know how REMOTE positions appear. Putting this as default
                workplaceType = job["location"]
                if workplaceType.upper() == "REMOTE":
                    accepts_remote = "Yes"
                else:
                    accepts_remote = "No"

                remote_office = is_remote_global(description)

                job_area = add_job_area(skills_required_format)

                if re.search(
                    r"\b(?:intern|internship|internships)\b",
                    title + " " + full_description,
                    re.IGNORECASE,
                ):
                    seniority = "Internship"
                elif re.search(
                    r"\b(?:junior)\b", title + " " + full_description, re.IGNORECASE
                ):
                    seniority = "Junior"
                else:
                    seniority = "With Experience"

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
                    r"\b(?:football|soccer|MLS)\b",
                    title + " " + description,
                    re.IGNORECASE,
                ):
                    sport_list += ["Football - Soccer"]
                elif re.search(
                    r"\b(?:football|NFL)\b", title + " " + description, re.IGNORECASE
                ):
                    sport_list += ["Football - NFL"]
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

                google_logo = search_for_png_image(job["company"])
                if google_logo:
                    logo = google_logo
                else:
                    logo = []

                if len(logo) > 0:
                    logo_permanent_url = logo[0]["url"]
                else:
                    logo_permanent_url = ""

                try:
                    salary = extract_salary(full_description)[0]
                except:
                    salary = None

                record = {
                    "Name": title,
                    "validated": True,
                    "Status": "Open",
                    "Start date": current_time,
                    "url": url,
                    "location": location,
                    "country": country,
                    "country_code": country_code,
                    "seniority": seniority,
                    "desciption": full_description,
                    "sport_list": sport_list,
                    "skills": skills_required_format,
                    "remote": accepts_remote,
                    "remote_office": remote_office,
                    "job_area": job_area,
                    "salary": str(salary),
                    "language": ["English"],
                    "company": job["company"],
                    "industry": industry,
                    "type": ["Permanent"],
                    "hours": ["Fulltime"],
                    "logo": logo,
                    "logo_permanent_url": logo_permanent_url,
                    "SEO:Index": "1",
                }
                table.create(record)
                record = {
                    "name": title,
                    "status": "Open",
                    "start_date": current_time,
                    "url": url,
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
                    "language": ["English"],
                    "company": job["company"],
                    "industry": industry[0] if industry else None,
                    "job_type": "Permanent",
                    "hours": "Fulltime",
                    "logo_permanent_url": logo_permanent_url,
                    "post_duration": 30,
                    "post_tier": "Free",
                    "featured": "1 - regular",
                    "creation_date": now,
                }

                insert_records(conn, "jobs", record)
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    # Ensure the connection is closed if still open
    if conn and conn.closed == 0:
        conn.close()
        print("Connection closed.")


# playonsports
# brooksrunning
# Kickoff
# gametime
# sportalliance EU


# playon = requests.get(f"https://api.lever.co/v0/postings/playonsports")

# brooksrunning = requests.get(f"https://api.lever.co/v0/postings/brooksrunning")

# kickoff = requests.get(f"https://api.lever.co/v0/postings/Kickoff")

# game_time = requests.get(f"https://api.lever.co/v0/postings/gametime")

# sportalliance = requests.get(f"https://api.eu.lever.co/v0/postings/sportalliance")

# ##
# fancode = requests.get(f"https://api.lever.co/v0/postings/dreamsports")

# grundens = requests.get(f"https://api.lever.co/v0/postings/Grundens")

# sporty = requests.get(f"https://api.lever.co/v0/postings/sporty")

# betr = requests.get(f"https://api.lever.co/v0/postings/betr")


# kitmanlabs = requests.get(f"https://api.lever.co/v0/postings/kitmanlabs")

# fnatic = requests.get(f"https://api.lever.co/v0/postings/fnatic")

# crossfit = requests.get(f"https://api.lever.co/v0/postings/crossfit")

# betstamp = requests.get(f"https://api.lever.co/v0/postings/Betstamp")
