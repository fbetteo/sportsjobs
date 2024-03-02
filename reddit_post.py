


import requests
import requests.auth

username = 'fark13'
subreddit = 'sports_jobs'
subreddit_display_name = 'SportsJobs.online'

client_auth = requests.auth.HTTPBasicAuth('NpCt949ZvDopgAztdKiDRg', 'LwBYGOZER_FrNaG1fX5xAZj5H0LYcg')
post_data = {"grant_type": "password", "username": "fark13", "password": "Carotex1"}
headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}
response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data)
response.json()

access_token = response.json()['access_token']
token_type = response.json()['token_type']

post_data = {
    "title": "Sports Jobs Test",
    "kind": "link",
    "sr": subreddit,
    "url": "http://www.sportsjobs.online",
    "resubmit": "true",
    "api_type": "json",
    "sendreplies": "true",
    "text": "tsting text"
}

requests.post("https://oauth.reddit.com/api/submit", 
              headers={"Authorization": "bearer " + access_token,
                        "User-Agent": "ChangeMeClient/0.1 by YourUsername"},
                          data=post_data)