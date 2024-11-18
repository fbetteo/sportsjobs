### Greenhouse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import html

from geopy.geocoders import Nominatim

import os
from pyairtable import Api
import requests
import requests.auth
import re
from dotenv import load_dotenv, find_dotenv

from utils import is_remote_global, add_job_area, search_for_png_image, find_country
import markdownify
import utils
from hetzner_utils import (
    start_postgres_connection,
    get_recent_urls,
    get_skills,
    insert_records,
)

from datetime import datetime

os.getcwd()

# load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/redditbot/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")

api = Api(AIRTABLE_TOKEN)
table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)


conn = start_postgres_connection()

# URLS POSTED IN THE LAST MONTH
# all = table.all(formula="{days_since_uploaded} < 30")
# recent_urls = [record["fields"]["url"] for record in all]
try:
    with conn as conn:
        recent_urls = get_recent_urls(conn)

        # LIST OF SKILLS AVAILABLE IN AIRTABLE
        # skills_column = [field for field in table.schema().fields if field.name == "skills"]
        # skills = [skill.name for skill in skills_column[0].options.choices]

        skills = get_skills(conn)

        # skill_to_remove = [
        #     "Data",
        #     "Media",
        #     "IT",
        #     "Sports",
        #     "Manager",
        #     "Gaming",
        #     "Social Media",
        #     "baseball",
        #     "kpi",
        #     "Networks",
        #     "Excel",
        #     "Powerpoint",
        #     "Analytics",
        #     "Statistics",
        # ]

        # for skill in skill_to_remove:
        #     skills.remove(skill)

        # skills_to_list_in_site = skills + skill_to_remove

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
        ]

        skills = skills + skills_to_search

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d")

        # find which companies post on lever
        # loop and extract postings related to Sports
        # post them if they are not on airtable
        # if they are on airtable, update the last updated date MAYBE

        response = requests.get(
            f"https://boards-api.greenhouse.io/v1/boards/majorleaguebaseball/jobs?content=true"
        )

        # decoded = html.unescape(asd.json()["jobs"][0]["content"])
        # soup = BeautifulSoup(decoded, "html.parser")
        # markdown_text = html_to_markdown(soup)
        # def clean_location(location):
        #     location = location.lower()
        #     location = location.split("/")[0]
        #     location = location.split("-")[0]
        #     location = location.split("or")[0]
        #     location = location.replace("remote", "")
        #     location = location.replace("hybrid", "")
        #     location = location.replace("in office", "")
        #     return location

        # def find_country(location_str):
        #     location_str = clean_location(location_str)
        #     geolocator = Nominatim(user_agent="sportsjobs")
        #     location = geolocator.geocode(
        #         location_str, exactly_one=True, addressdetails=True, language="en"
        #     )

        #     if location:
        #         # Access the address dictionary
        #         address = location.raw.get("address", {})
        #         # Get the country
        #         country = address.get("country", "Country not found")
        #         return country
        #     else:
        #         return "united states"

        # Example usage

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

        companies = {
            "The Score": {
                "greenhouse_name": "scoremediaandgaminginc",
                "logo": [
                    {
                        "url": "https://play-lh.googleusercontent.com/dDjFtNHe0GExF_0ldvkanmLP3MR3khTepvsn_HrlwsKX7-50itYY3YT1ohxsvmyhcg",
                        "filename": "theScore.png",
                    }
                ],
            },
            "Urban Sports Club": {
                "greenhouse_name": "urbansportsclub",
                "logo": [
                    {
                        "url": "https://s2-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/761/500/resized/1616171296475.jpeg?1633091741",
                        "filename": "urban_sports_club.png",
                    }
                ],
            },
            "Genius Sports": {
                "greenhouse_name": "geniussports",
                "logo": [
                    {
                        "url": "https://s3-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/097/300/resized/Logo_genius_1.png?1626023064",
                        "filename": "genius_sports.png",
                    }
                ],
            },
            "Golden State Warriors": {
                "greenhouse_name": "goldenstatewarriors",
                "logo": [
                    {
                        "url": "https://upload.wikimedia.org/wikipedia/en/thumb/0/01/Golden_State_Warriors_logo.svg/1200px-Golden_State_Warriors_logo.svg.png",
                        "filename": "golden_state_warriors.png",
                    }
                ],
            },
            "UnderDog Fantasy": {
                "greenhouse_name": "underdogfantasy",
                "logo": [
                    {
                        "url": "https://s5-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/278/300/resized/Main_Logo.png?1656375980",
                        "filename": "underdog_fantasy.png",
                    }
                ],
            },
            "Zelus Analytics": {
                "greenhouse_name": "zelusanalytics",
                "logo": [
                    {
                        "url": "https://media.licdn.com/dms/image/C4D0BAQGpEcNUokAFNA/company-logo_200_200/0/1630558648297/zelus_analytics_logo?e=2147483647&v=beta&t=GbnYvq4etaKk26yby2FgevjeLQBsR7oAY5AcX9sTM0I",
                        "filename": "zelus_analytics.png",
                    }
                ],
            },
            "Barstool Sports": {
                "greenhouse_name": "barstoolsports",
                "logo": [
                    {
                        "url": "https://www.barstoolsports.com/static/images/logo-white.png",
                        "filename": "barstool_sports.png",
                    }
                ],
            },
            # "Lear Field": {
            #     "greenhouse_name": "learfield",
            #     "logo": [
            #         {
            #             "url": "https://cdn.learfield.com/wp-content/uploads/2023/12/Learfield_Logo_White-1.png",
            #             "filename": "lear_field.png",
            #         }
            #     ],
            # },
            "Excel Sports Management": {
                "greenhouse_name": "excelsportsmanagement",
                "logo": [
                    {
                        "url": "https://s5-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/440/800/resized/EXCEL_SPORTS_MANAGEMENT__LLC-1553200528-85460.png?1665090576",
                        "filename": "excelsportsmanagement.png",
                    }
                ],
            },
            "Monumental Sports & Entertainment": {
                "greenhouse_name": "monumentalsports",
                "logo": [
                    {
                        "url": "https://s7-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/381/000/resized/Monumental-Logo-Large-Light-Background.png?1701188822",
                        "filename": "monumental_sports_entertainment.png",
                    }
                ],
            },
            # "FanDuel": {
            #     "greenhouse_name": "fanduel",
            #     "logo": [
            #         {
            #             "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAbFBMVEUAce4Ab+4AbO4Aau0AaO0AZu0AZO0ddu55o/Kqw/XG1/ja5fnm7fqzyfYAX+27zvcnee6eu/T///3///xZkfFll/E7gvDD1Pj9//zt8/sAVOz2+fyQsvRAhPDf6PmFqvNunfKauPQAWuwAY+1/YJLWAAABKUlEQVR4Aa2RRaIDIRBEYbDRSDEaHbn/HX9Dx2X1UxvkNVSL+L9korSxSmiVyBeirEuzvCir1TpLN1bJOzJuWwLwHnUDUrl15oJl2xHoSX7YFWHjga5laveIBMDW4Rq3twwHOgL5oaHoY3PIAYIDQ3PyPc7GxDQpaWPO6P3JRKg7gmMilU44iWQk2Om4VxPts7k95GemOqPoSXG2NcGhAJAyXEqC9aUWExLw/fVCtqA9W7IpyYNrM5Vny9u/pC7lhwLXT24mfj2zo+3oUC5MOHcKblTMvQn7kQM5OrbUhSa44F7Yx5FtYseklEns5eZppOpMFFvtIkuVeJKt0Pt83gdWWfGipYMf5jCDjjN9pmvATUDF7JUeMG1wsOKj9LEzrRJfJDU17yf6A4tMGL31Dd89AAAAAElFTkSuQmCC",
            #             "filename": "fanduel.png",
            #         }
            #     ],
            # },
            "Swish Analytics": {
                "greenhouse_name": "swishanalytics",
                "logo": [
                    {
                        "url": "https://s5-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/119/500/resized/Swish-Logo-2023-Black-Square-2.jpg?1693486896",
                        "filename": "swish_analytics.png",
                    }
                ],
            },
            "Catapult Sports": {
                "greenhouse_name": "catapultsports",
                "logo": [
                    {
                        "url": "https://recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/000/010/502/resized/Catapult_logo_-_black.png?1634256060",
                        "filename": "catapult_sports.png",
                    }
                ],
            },
            "Kaizen Gaming": {
                "greenhouse_name": "kaizengaming",
                "logo": [
                    {
                        "url": "https://productioncms.kaizengaming.com/uploads/header_Logo_b1c17ae784.svg",
                        "filename": "kaizen_gaming.png",
                    }
                ],
            },
            "The Florida Panthers": {
                "greenhouse_name": "thefloridapanthers",
                "logo": [
                    {
                        "url": "https://s6-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/048/500/resized/panthers_logo_2.png?1672848760",
                        "filename": "florida_panthers.png",
                    }
                ],
            },
            "MLB": {
                "greenhouse_name": "majorleaguebaseball",
                "logo": [
                    {
                        "url": "https://images.ctfassets.net/iiozhi00a8lc/VtQp1Uvhf7RPuqOjXgk2N/3527993b96002b528239944121b9c512/1.svg",
                        "filename": "mlb.png",
                    }
                ],
            },
            "Second Spectrum": {
                "greenhouse_name": "secondspectrum",
                "logo": [
                    {
                        "url": "",
                        "filename": "second_spectrum.png",
                    }
                ],
            },
            "Tempus Ex": {
                "greenhouse_name": "txm",
                "logo": [
                    {
                        "url": "https://s3-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/014/700/resized/txm-logo.png?1619552318",
                        "filename": "tempus_ex.png",
                    }
                ],
            },
            "Wargaming": {
                "greenhouse_name": "wargamingen",
                "logo": [
                    {
                        "url": "https://logo.clearbit.com/https://wargaming.com/",
                        "filename": "wargaming.png",
                    }
                ],
            },
            "Epic Games": {
                "greenhouse_name": "epicgames",
                "logo": [
                    {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Epic_Games_logo.svg/150px-Epic_Games_logo.svg.png",
                        "filename": "epicgames.png",
                    }
                ],
            },
            "Los Angeles Clippers": {
                "greenhouse_name": "laclippers",
                "logo": [
                    {
                        "url": "https://upload.wikimedia.org/wikipedia/en/thumb/e/ed/Los_Angeles_Clippers_%282024%29.svg/220px-Los_Angeles_Clippers_%282024%29.svg.png",
                        "filename": "laclippers.png",
                    }
                ],
            },
            "Madison Square Garden": {
                "greenhouse_name": "msgsports",
                "logo": [
                    {
                        "url": "https://www.msgsports.com/wp-content/uploads/2020/03/MadisonSquareGarden_Sports_Logo_White.png",
                        "filename": "msg.png",
                    }
                ],
            },
            "NFL": {
                "greenhouse_name": "nflcareers",
                "logo": [
                    {
                        "url": "https://s8-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/029/800/resized/LOGO.png?1716219119",
                        "filename": "nfl.png",
                    }
                ],
            },
            "Philadelphia Eagles": {
                "greenhouse_name": "philadelphiaeagles",
                "logo": [
                    {
                        "url": "https://s6-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/224/900/resized/Diving_Eagle_Head.jpg?1678976564",
                        "filename": "philadelphia_eagles.png",
                    }
                ],
            },
        }

        for company, attributes in companies.items():

            response = requests.get(
                f"https://boards-api.greenhouse.io/v1/boards/{attributes['greenhouse_name']}/jobs?content=true"
            )

            if response.status_code != 200:
                print(f"Error in request for {company}")
                continue

            for job in response.json()["jobs"]:

                description = job["content"]
                # list_text = ""
                # for list_topics in job["lists"]:

                #     for k, v in list_topics.items():
                #         v = v.replace("<li>", "* ").replace("</li>", "  \n")
                #         list_text += v + "\n"

                # soup = BeautifulSoup(list_text, "html.parser")
                # soup_parsed = soup.get_text()
                decoded = html.unescape(description)

                full_description = markdownify.markdownify(decoded, heading_style="ATX")

                # Just techinical skills we want to filter by
                pattern = r"\b(?:" + "|".join(skills_to_search) + r")\b"
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

                none_skill = len(skills_required) < 2

                if (job["absolute_url"] in recent_urls) or (none_skill):
                    continue

                # Duplicate but to add all skills. I should create a function to avoid duplicating.
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

                title = job["title"]
                createdAt = job["updated_at"]
                url = job["absolute_url"]
                location = job["location"]["name"]

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

                salary_data = job.get("pay_input_ranges", [])
                if len(salary_data) > 0:
                    salary = salary_data[0].get("max_cents", None)
                    try:
                        salary = int(salary) / 100
                    except:
                        salary = None
                else:
                    salary = None

                if not salary:
                    try:
                        salary = utils.extract_salary(full_description)[0]
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
                    "company": company,
                    "industry": industry,
                    "type": ["Permanent"],
                    "hours": [hours],
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
    print(f"Error occurred: {e}")
finally:
    # Ensure the connection is closed if still open
    if conn and conn.closed == 0:
        conn.close()
        print("Connection closed.")
