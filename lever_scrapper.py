import requests
from bs4 import BeautifulSoup


import os
from pyairtable import Api
import requests
import requests.auth
import re
from dotenv import load_dotenv, find_dotenv
os.getcwd()

load_dotenv(find_dotenv("C:/Users/Franco/Desktop/data_science/redditbot/.env"))

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_JOBS_TABLE = os.getenv("AIRTABLE_JOBS_TABLE")

api = Api(AIRTABLE_TOKEN)
table = api.table(AIRTABLE_BASE, AIRTABLE_JOBS_TABLE)

from datetime import datetime

# URLS POSTED IN THE LAST MONTH
all = table.all(formula = "{days_since_uploaded} < 30")
recent_urls = [record['fields']['url'] for record in all]

# LIST OF SKILLS AVAILABLE IN AIRTABLE
skills_column = [ field for field in table.schema().fields if field.name == 'skills']
skills = [skill.name for skill in skills_column[0].options.choices]

now = datetime.now()
current_time = now.strftime("%Y-%m-%d")

# find which companies post on lever
# loop and extract postings related to Sports
# post them if they are not on airtable
# if they are on airtable, update the last updated date MAYBE

companies = {
    'The Athletic': {
        'lever_name': 'theathletic',
        'logo': [{"url":"https://lever-client-logos.s3.us-west-2.amazonaws.com/8ff13c41-d891-40d4-b9d8-de9c995ff06f-1600385441351.png",
             "filename": "theathletic.png"}]
    },
    'PlayOn! Sports': {
        'lever_name': 'playonsports',
        'logo': [{"url":"https://lever-client-logos.s3.us-west-2.amazonaws.com/41a41462-61a1-46dd-9190-73fd66fa11ee-1656096708496.png",
             "filename": "playonsports.png"}]
    },
    'Brooks Running': {
        'lever_name': 'brooksrunning',
        'logo': [{"url":"https://lever-client-logos.s3.amazonaws.com/f0a2961a-09a7-412e-9b8f-0d186769bc1a-1501529042183.png",
             "filename": "brooksrunning.png"}]
    },
    'Kickoff': {
        'lever_name': 'Kickoff',
        'logo': [{"url":"https://lever-client-logos.s3.us-west-2.amazonaws.com/537a8842-2bd0-43b4-bb27-fc6c26450c29-1706218622648.png",
             "filename": "kickoff.png"}]
    },
    'GameTime': {
        'lever_name': 'gametime',
        'logo': [{"url":"https://lever-client-logos.s3.amazonaws.com/a0ca3046-353c-409d-bf49-22a954da734a-1568149219931.png",
             "filename": "gametime.png"}]
    },
    'SportAlliance': {
        'lever_name': 'sportalliance',
        'logo': [],
        'europe': True
    },
    'Dream Sports': {
        'lever_name': 'dreamsports',
        'logo': [{"url":"https://lever-client-logos.s3-us-west-2.amazonaws.com/58d80c3e-b78b-4751-b256-c1dd090370f2-1588151685110.png",
             "filename": "dreamsports.png"}]
    },
    'Grundens': {
        'lever_name': 'Grundens',
        'logo': [{"url":"https://lever-client-logos.s3.us-west-2.amazonaws.com/c7c1d8a4-cf7f-459f-8422-96ab19215b0f-1612978037834.png",
             "filename": "grundens.png"}]
    },
    'Sporty': {
        'lever_name': 'sporty',
        'logo': [{"url":"https://lever-client-logos.s3.us-west-2.amazonaws.com/6616a346-760f-4098-a325-0a582aa0542e-1608646767819.png",
             "filename": "sporty.png"}]
    },
    'Betr'  : { 
        'lever_name': 'betr',
        'logo': [{"url":"https://lever-client-logos.s3.us-west-2.amazonaws.com/56f26027-121f-4868-938c-ba9bdef5c57c-1658709755202.png",
             "filename": "betr.png"}]
    },
    'Kitman Labs': {
        'lever_name': 'kitmanlabs',
        'logo': [{"url":"https://lever-client-logos.s3.us-west-2.amazonaws.com/00b27a9e-32b0-4248-b224-5147ecacd464-1688118163729.png",
             "filename": "kitmanlabs.png"}]
    },
    'Fnatic': {
        'lever_name': 'fnatic',
        'logo': [{"url":"https://lever-client-logos.s3.amazonaws.com/80d1f71b-c66f-4193-8bb1-85dfda9a629e-1580903456170.png",
             "filename": "fnatic.png"}]
    },
    'CrossFit': {
        'lever_name': 'crossfit',
        'logo': [{"url":"https://lever-client-logos.s3.us-west-2.amazonaws.com/7744085c-b7f6-4d4a-b5b2-9f310e0bb564-1646405943505.png",
             "filename": "crossfit.png"}]
    },
    'Betstamp': {
        'lever_name': 'Betstamp',
        'logo': [{"url":"https://lever-client-logos.s3.us-west-2.amazonaws.com/ccfa9849-85c7-4334-994a-e2eb3f913c54-1633288684940.png",
             "filename": "betstamp.png"}]
    }
}

for company, attributes in companies.items():

    if not attributes.get('europe', False):
        response = requests.get(f"https://api.lever.co/v0/postings/{attributes['lever_name']}")
    else:
        response = requests.get(f"https://api.eu.lever.co/v0/postings/{attributes['lever_name']}")

    for job in response.json():
        
        description = job['descriptionPlain'] 
        list_text = ''
        for list_topics in job['lists']:
            
            for k,v in list_topics.items():
                v = v.replace("<li>", "* ").replace("</li>", "  \n")
                list_text += v + "\n"
            

        soup = BeautifulSoup(list_text, 'html.parser')
        soup_parsed = soup.get_text()

        full_description = f"""{description} 
          {soup_parsed}"""
        
        pattern = r'\b(?:' + '|'.join(skills) + r')\b'
        skills_required = [skill.lower() for skill in set(re.findall(pattern, full_description, re.IGNORECASE))]
        skills_required_format = [skill for skill in skills if skill.lower() in skills_required]


        none_skill = len(skills_required) == 0

        if (job['hostedUrl'] in recent_urls) or (none_skill):
            continue

        title  = job['text']
        createdAt = job['createdAt']
        url = job['hostedUrl']
        location = job['categories']['allLocations']
        country = job['country']
        workplaceType = job['workplaceType']
        if workplaceType.upper() == 'REMOTE':
            accepts_remote = 'Yes'
        else:
            accepts_remote = 'No'
        
        
        if re.search(r'\b(?:junior)\b', title + " " + description, re.IGNORECASE):
            seniority = "Junior"
        elif re.search(r'\b(?:intern|internship)\b', title + " " + description, re.IGNORECASE):
            seniority = "Internship"
        else: 
            seniority = "With Experience"

        


        record = {
            'Name': title,
            'validated': True,
            'Status': 'Open',
            'Start date': current_time,
            'url': url,
            'location': location[0],
            'seniority': seniority,
            'desciption': full_description,
            'skills': skills_required_format,
            'remote': accepts_remote,
            'salary': None,
            'language': ['English'],
            'company': company,
            'type': ['Permanent'],
            'hours': ['Fulltime'],
            'logo': attributes.get('logo', []),
            'SEO:Index': "1"

        }
        table.create(record)



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
        
crossfit = requests.get(f"https://api.lever.co/v0/postings/crossfit")

betstamp = requests.get(f"https://api.lever.co/v0/postings/Betstamp")