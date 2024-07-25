import tweepy
from datetime import datetime
import os


# PROBLEM: THIS WORKS BUT IT IS LINKED TO MY PERSONAL TWITTER ACCOUNT
# NEED TO GET A DIFFERENT DEV ACCOUNT FOR THE BOT MAYBE (IN ANOTHER EMAIL) OR HACK MY WAY AROUND IT
# BUT SEEMS COMPLICATED

api_key = os.getenv("TWITTER_CONSUMER_KEY")
api_secret = os.getenv("TWITTER_SECRET_KEY")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
access_token
api = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_secret,
    bearer_token=bearer_token,
)

api.get_me()
# api.create_tweet(text="test")
